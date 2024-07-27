import typing as t
import uuid as uuid_gen
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pymysql.err
import pytz
import requests
import sqlalchemy.orm
from _decimal import ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from OpenSSL.crypto import Error as OpenSSLCryptoError
from sqlalchemy import func, orm
from sqlalchemy import sql

from backend import efi_xml
from backend import enums
from backend import fiskalizacija
from backend import i18n
from backend import stampa
from backend.db import db
from backend.logging import logger
from backend.models import Artikal, OrdinalNumberCounter
from backend.models import Depozit
from backend.models import Faktura
from backend.models import FakturaGrupaPoreza
from backend.models import FakturaMailKampanja
from backend.models import FakturaMailKampanjaStavka
from backend.models import FakturaStavka
from backend.models import FakturaTip
from backend.models import Firma
from backend.models import InvoiceItemCorrectionType
from backend.models import InvoiceProcessingLock
from backend.models import InvoiceSchedule
from backend.models import JedinicaMjere
from backend.models import Komitent
from backend.models import MagacinZaliha
from backend.models import NaplatniUredjaj
from backend.models import Operater
from backend.models import PaymentMethod
from backend.models import PaymentMethodType
from backend.models import RegisterInvoiceRequest
from backend.models import RegisterInvoiceResponse
from backend.models import TaxExemptionReason
from backend.models import Valuta
from backend.opb import certificate_opb
from backend.opb import depozit_opb
from backend.opb import firma_opb
from backend.opb.helpers import InvoiceFilterData
from backend.opb.helpers import danas_filteri
from backend.opb.helpers import get_efi_verify_url
from backend.podesavanja import podesavanja


class InvoiceProcessingException(Exception):

    def __init__(self, messages, invoice=None, original_exception=None, locale=i18n.DEFAULT_LOCALE):
        self.invoice = invoice
        self.messages = messages
        self.original_exception = original_exception

        super(InvoiceProcessingException, self).__init__(self.get_message(locale))

    def get_message(self, locale: str = i18n.DEFAULT_LOCALE) -> str:
        return self.messages.get(locale)


class InvoiceProcessing:

    def __init__(self, locale=i18n.DEFAULT_LOCALE):
        self.locale = locale
        self.is_success = False
        self.messages = None

    def get_message(self, locale: str = i18n.DEFAULT_LOCALE) -> str:
        return self.messages[locale]

    @contextmanager
    def acquire_lock(self, payment_device_id: int, session: sqlalchemy.orm.Session = None, safe=True):
        session = session or db.create_session()

        try:
            # TODO This lock is not good enough. Must be locked based on invoice id.
            session.get(InvoiceProcessingLock, payment_device_id, with_for_update=True)
        except pymysql.err.OperationalError:
            session.commit()
            raise
        except Exception:
            session.commit()
            raise

        try:
            yield session
            self.is_success = True
            self.messages = {
                i18n.LOCALE_SR_LATN_ME: 'Faktura je fiskalizovana.',
                i18n.LOCALE_EN_US: 'Invoice is fiscalised.',
            }
        except InvoiceProcessingException as exception:
            self.is_success = False
            self.messages = exception.messages
        except (Exception, ):
            logger.exception('Nepoznata greška prilikom fiskalizacije.')
            self.is_success = False
            self.messages = {
                i18n.LOCALE_SR_LATN_ME: 'Došlo je do nepredviđene greške. Molimo kontaktirajte tehničku podršku.',
                i18n.LOCALE_EN_US: 'Unknown error occurred. Please contact technical support.',
            }

            if not safe:
                raise
        finally:
            session.commit()

    @property
    def message(self):
        return self.get_message()


def _needs_and_has_cash_deposit_or_raise(invoice):
    if not invoice.is_cash:
        return

    current_deposit = depozit_opb.listaj_danasnji_depozit(invoice.naplatni_uredjaj_id)
    if current_deposit is None:
        if invoice.naplatni_uredjaj.podrazumijevani_iznos_depozita is not None:
            current_deposit = Depozit()
            current_deposit.operater = invoice.operater
            current_deposit.firma = invoice.firma
            current_deposit.je_pocetak_dana = True
            current_deposit.tip_depozita = Depozit.TIP_DEPOZITA_INITIAL
            current_deposit.naplatni_uredjaj = invoice.naplatni_uredjaj
            current_deposit.iznos = invoice.naplatni_uredjaj.podrazumijevani_iznos_depozita
            current_deposit.status = 1
            db.session.add(current_deposit)
            db.session.commit()
        else:
            raise InvoiceProcessingException(
                messages={
                    i18n.LOCALE_SR_LATN_ME:
                        'Račun se ne može fiskalizovati jer gotovinski depozit nije registrovan za ovaj naplatni '
                        'uređaj. Registrujte depozit pa pokušajte ponovo.',
                    i18n.LOCALE_EN_US:
                        'Invoice cannot be fiscalised because cash deposit is not register for this payment device. '
                        'Register deposit then try again.'
                }
            )

    if current_deposit.status != Depozit.STATUS_FISCALISE_SUCCESS:
        current_deposit = depozit_opb.efi_prijava_depozita(current_deposit, invoice.firma)

        if isinstance(current_deposit, Depozit):
            return

        raise InvoiceProcessingException(
            messages={
                i18n.LOCALE_SR_LATN_ME:
                    'Račun se ne može fiskalizovati jer gotovinski depozit nije registrovan za ovaj naplatni uređaj. '
                    'Registrujte depozit pa pokušajte ponovo.',
                i18n.LOCALE_EN_US:
                    'Invoice cannot be fiscalised because cash deposit is not register for this payment device. '
                    'Register deposit then try again.'
            }
        )


def exists_at_least_one_cash_invoice_for_current_day(naplatni_uredjaj_id: int) -> bool:
    day_start, next_day_start = danas_filteri()

    return 1 == db.session.query(Faktura.id) \
        .filter(Faktura.datumfakture >= day_start, Faktura.datumfakture < next_day_start) \
        .filter(Faktura.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(Faktura.status == Faktura.STATUS_FISCALISATION_SUCCESS) \
        .filter(Faktura.tip_fakture_id.notin_([Faktura.TYPE_INVOICE_TEMPLATE])) \
        .filter(Faktura.is_cash.is_(True)) \
        .limit(1) \
        .count()


def listaj_fakturu_po_idu(faktura_id):
    return db.session.query(Faktura) \
        .filter(Faktura.id == faktura_id) \
        .first()


def listaj_fakturu_po_ikofu(faktura_ikof) -> Faktura:
    # TODO: Ovaj poziv je veoma sport, potrebno ga je optimizovati
    return db.session.query(Faktura) \
        .filter(Faktura.ikof == faktura_ikof) \
        .first()


def get_invoice_by_company_id_and_iic(company_id, iic) -> Faktura:
    # TODO: DUPLICATE listaj_fakturu_po_ikofu
    return db.session.query(Faktura) \
        .filter(Faktura.firma_id == company_id) \
        .filter(Faktura.ikof == iic) \
        .filter(Faktura.status == 2) \
        .first()


def get_invoice_by_company_tin_and_iic(company_tin, iic) -> Faktura:
    return db.session.query(Faktura) \
        .filter(Faktura.firma.has(Firma.pib == company_tin)) \
        .filter(Faktura.ikof == iic) \
        .filter(Faktura.status == 2) \
        .first()


def listaj_efi_odgovor(faktura_id):
    return db.session.query(RegisterInvoiceResponse) \
        .filter(RegisterInvoiceResponse.faktura_id == faktura_id) \
        .first()


def listaj_tip_fakture_po_idu(faktura_tip_id):
    return db.session.query(FakturaTip) \
        .filter(FakturaTip.id == faktura_tip_id) \
        .first()


def get_payment_method_type_by_id(payment_method_type_id: int) -> t.Optional[PaymentMethodType]:
    return db.session.query(PaymentMethodType) \
        .filter(PaymentMethodType.id == payment_method_type_id) \
        .first()


def get_filtered_invoices_count(
        payment_device_id: int,
        filters: InvoiceFilterData,
        customer_invoice_view: enums.CustomerInvoiceView
):
    query = db.session.query(Faktura.id)
    query_with_filters = add_invoice_filters_to_query(query, payment_device_id, filters, customer_invoice_view)
    return query_with_filters.count()


def get_filtered_invoices(
        payment_device_id: int,
        filters: InvoiceFilterData,
        customer_invoice_view: enums.CustomerInvoiceView
):
    query = db.session.query(
        Faktura.id
    )
    base_query_with_filters = add_invoice_filters_to_query(query, payment_device_id, filters, customer_invoice_view) \
        .order_by(func.year(Faktura.datumfakture).desc(), Faktura.efi_ordinal_number.desc()) \
        .limit(filters.broj_stavki_po_stranici) \
        .offset((filters.broj_stranice - 1) * filters.broj_stavki_po_stranici)

    items = base_query_with_filters.all()

    return items



def add_invoice_filters_to_query(
        query: orm.Query,
        naplatni_uredjaj_id: int,
        filters: InvoiceFilterData,
        customer_invoice_view: enums.CustomerInvoiceView
):
    q1 = query \
        .filter(Faktura.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(Faktura.status.in_([
            Faktura.STATUS_FISCALISATION_SUCCESS,
            Faktura.STATUS_CANCELLED,
            Faktura.STATUS_IN_CREDIT_NOTE,
            Faktura.STATUS_HAS_ERROR_CORRECTIVE
        ]))

    if filters.ordinal_id is not None:
        q1 = q1.filter(Faktura.efi_ordinal_number == filters.ordinal_id)

    if filters.total_price_gte is not None:
        q1 = q1.filter(Faktura.korigovana_ukupna_cijena_prodajna >= filters.total_price_gte)

    if filters.total_price_lte is not None:
        q1 = q1.filter(Faktura.korigovana_ukupna_cijena_prodajna <= filters.total_price_lte)

    if filters.fiscalization_date_gte is not None:
        q1 = q1.filter(Faktura.datumfakture >= filters.fiscalization_date_gte)

    if filters.fiscalization_date_lte is not None:
        q1 = q1.filter(Faktura.datumfakture <= filters.fiscalization_date_lte)

    if len(filters.payment_type_ids) > 0:
        q1 = q1.filter(
            Faktura.payment_methods.any(PaymentMethod.payment_method_type_id.in_(filters.payment_type_ids)))

    if len(filters.not_payment_type_ids) > 0:
        q1 = q1.filter(
            Faktura.payment_methods.any(PaymentMethod.payment_method_type_id.notin_(filters.not_payment_type_ids)))

    if len(filters.client_ids) > 0:
        q1 = q1.filter(Faktura.komitent_id.in_(filters.client_ids))

    if len(filters.invoice_type_ids) > 0:
        q1 = q1.filter(
            sql.or_(
                Faktura.tip_fakture_id.in_(filters.invoice_type_ids)
            )
        )

    if len(filters.not_invoice_type_ids) > 0:
        q1 = q1.filter(
            sql.or_(
                Faktura.tip_fakture_id.notin_(filters.not_invoice_type_ids)
            )
        )

    if len(filters.invoice_ids) > 0:
        q1 = q1.filter(Faktura.id.in_(filters.invoice_ids))

    if len(filters.not_invoice_ids) > 0:
        q1 = q1.filter(Faktura.id.notin_(filters.not_invoice_ids))

    if len(filters.statuses) > 0:
        q1 = q1.filter(Faktura.status.in_(filters.statuses))

    if len(filters.not_statuses) > 0:
        q1 = q1.filter(Faktura.status.notin_(filters.not_statuses))

    q1 = q1.filter(Faktura.customer_invoice_view == customer_invoice_view.value)

    return q1


def get_invoice_filter_query(
        firma_id: int,
        naplatni_uredjaj_id: int,
        filters: InvoiceFilterData,
        customer_invoice_view: enums.CustomerInvoiceView
):
    q1 = db.session.query(Faktura) \
        .filter(Faktura.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(Faktura.status.in_([
            Faktura.STATUS_FISCALISATION_SUCCESS,
            Faktura.STATUS_CANCELLED,
            Faktura.STATUS_IN_CREDIT_NOTE,
            Faktura.STATUS_HAS_ERROR_CORRECTIVE
        ]))

    if filters.ordinal_id is not None:
        q1 = q1.filter(Faktura.efi_ordinal_number == filters.ordinal_id)

    if filters.total_price_gte is not None:
        q1 = q1.filter(Faktura.korigovana_ukupna_cijena_prodajna >= filters.total_price_gte)

    if filters.total_price_lte is not None:
        q1 = q1.filter(Faktura.korigovana_ukupna_cijena_prodajna <= filters.total_price_lte)

    if filters.fiscalization_date_gte is not None:
        q1 = q1.filter(Faktura.datumfakture >= filters.fiscalization_date_gte)

    if filters.fiscalization_date_lte is not None:
        q1 = q1.filter(Faktura.datumfakture <= filters.fiscalization_date_lte)

    if len(filters.payment_type_ids) > 0:
        q1 = q1.filter(
            Faktura.payment_methods.any(PaymentMethod.payment_method_type_id.in_(filters.payment_type_ids)))

    if len(filters.not_payment_type_ids) > 0:
        q1 = q1.filter(
            Faktura.payment_methods.any(PaymentMethod.payment_method_type_id.notin_(filters.not_payment_type_ids)))

    if len(filters.client_ids) > 0:
        q1 = q1.filter(Faktura.komitent_id.in_(filters.client_ids))

    if len(filters.invoice_type_ids) > 0:
        q1 = q1.filter(
            sql.or_(
                Faktura.tip_fakture_id.in_(filters.invoice_type_ids)
            )
        )

    if len(filters.not_invoice_type_ids) > 0:
        q1 = q1.filter(
            sql.or_(
                Faktura.tip_fakture_id.notin_(filters.not_invoice_type_ids)
            )
        )

    if len(filters.invoice_ids) > 0:
        q1 = q1.filter(Faktura.id.in_(filters.invoice_ids))

    if len(filters.not_invoice_ids) > 0:
        q1 = q1.filter(Faktura.id.notin_(filters.not_invoice_ids))

    if len(filters.statuses) > 0:
        q1 = q1.filter(Faktura.status.in_(filters.statuses))

    if len(filters.not_statuses) > 0:
        q1 = q1.filter(Faktura.status.notin_(filters.not_statuses))

    q1 = q1.filter(Faktura.customer_invoice_view == customer_invoice_view.value)

    return q1.order_by(func.year(Faktura.datumfakture).desc(), Faktura.efi_ordinal_number.desc())


def get_next_ordinal_number(type_id: int, payment_device_id: int, year: int, session: sqlalchemy.orm.Session):
    counter = session.query(OrdinalNumberCounter) \
        .filter(OrdinalNumberCounter.type_id == type_id) \
        .filter(OrdinalNumberCounter.payment_device_id == payment_device_id) \
        .filter(OrdinalNumberCounter.year == year) \
        .first()

    if counter is None or counter.year != year:
        # Create counter using new session, because it must be commited
        counter = OrdinalNumberCounter()
        counter.type_id = type_id
        counter.payment_device_id = payment_device_id
        counter.year = year
        counter.last_value = 0

    counter.last_value += 1
    session.add(counter)
    return counter.last_value


def get_efi_ordinal_number(invoice: Faktura, year: int, session: sqlalchemy.orm.Session):
    return get_next_ordinal_number(
        type_id=enums.OrdinalNumberCounterType.EFI_COUNT.value,
        payment_device_id=invoice.naplatni_uredjaj_id,
        year=year,
        session=session
    )


def get_internal_ordinal_number(invoice: Faktura, year: int, session: sqlalchemy.orm.Session):
    if invoice.tip_fakture_id == Faktura.TYPE_ADVANCE:
        type_id = enums.OrdinalNumberCounterType.ADVANCE_INVOICES.value
    elif invoice.tip_fakture_id == Faktura.TYPE_REGULAR:
        type_id = enums.OrdinalNumberCounterType.REGULAR_INVOICES.value
    elif invoice.tip_fakture_id == Faktura.TYPE_ORDER:
        type_id = enums.OrdinalNumberCounterType.ORDER_INVOICES.value
    elif invoice.tip_fakture_id == Faktura.TYPE_CORRECTIVE or invoice.tip_fakture_id == Faktura.TYPE_ERROR_CORRECTIVE:
        if invoice.korigovana_faktura is not None:
            if invoice.korigovana_faktura.tip_fakture_id == Faktura.TYPE_REGULAR:
                type_id = enums.OrdinalNumberCounterType.REGULAR_INVOICES.value
            elif invoice.korigovana_faktura.tip_fakture_id == Faktura.TYPE_ADVANCE:
                type_id = enums.OrdinalNumberCounterType.ADVANCE_INVOICES.value
            else:
                raise ValueError("Unhandled invoice type for internal counter value.")
        elif invoice.corrected_credit_note is not None:
            type_id = enums.OrdinalNumberCounterType.CREDIT_NOTES.value
        else:
            raise ValueError("Unhandled invoice type for internal counter value.")
    else:
        raise ValueError("Unhandled invoice type for internal counter value.")

    return get_next_ordinal_number(
        type_id=type_id,
        payment_device_id=invoice.naplatni_uredjaj_id,
        year=year,
        session=session
    )


def get_payment_method_from_dict(data: dict):
    payment_method_type = get_payment_method_type_by_id(data.get('payment_method_type_id'))
    if payment_method_type is None:
        raise InvoiceProcessingException(
            messages={
                i18n.LOCALE_SR_LATN_ME: 'Faktura nije fiskalizovana jer nedostaje vrsta plaćanja.',
                i18n.LOCALE_EN_US: 'Invoice was not fiscalised because it is missing payment type.',
            }
        )

    payment_method = PaymentMethod()
    payment_method.payment_method_type = payment_method_type
    payment_method.payment_method_type_id = payment_method_type.id
    payment_method.amount = data.get('amount')
    advance_invoice_dict = data.get('advance_invoice')

    if advance_invoice_dict is not None:
        _advance_invoice_id = advance_invoice_dict['id']
        advance_invoice = db.session.query(Faktura).get(_advance_invoice_id)

        # TODO Security issue, check if same company

        if advance_invoice is None:
            raise InvoiceProcessingException(
                messages={
                    i18n.LOCALE_SR_LATN_ME: "Nije odabrana avansna faktura.",
                    i18n.LOCALE_EN_US: "Advance invoice is not defined."
                }
            )
        payment_method.advance_invoice_id = _advance_invoice_id
        payment_method.advance_invoice = advance_invoice

    return payment_method


def get_payment_methods_from_dict(data: dict):
    data = data.get('payment_methods')
    if not isinstance(data, list) or len(data) == 0:
        raise InvoiceProcessingException(
            messages={
                i18n.LOCALE_SR_LATN_ME: 'Faktura nije fiskalizovana jer nedostaje vrsta plaćanja.',
                i18n.LOCALE_EN_US: 'Invoice was not fiscalised because it is missing payment type.',
            }
        )

    for row in data:
        yield get_payment_method_from_dict(row)


def get_currency_from_dict(data: dict) -> Valuta:
    return db.session.query(Valuta).get(data['valuta_id'])


def get_buyer_by_id(company: Firma, buyer_id: int) -> t.Optional[Komitent]:
    komitent = firma_opb.get_buyer_by_id(buyer_id)

    if komitent is None or komitent.pibvlasnikapodatka != company.pib:
        raise InvoiceProcessingException(
            messages={
                i18n.LOCALE_SR_LATN_ME: "Kupac nije pronađen.",
                i18n.LOCALE_EN_US: "Buyer data is missing."
            }
        )

    return komitent


def get_datum_prometa_from_dict(data: dict) -> t.Optional[datetime]:
    datum_prometa = data.get('datum_prometa')
    if datum_prometa is not None:
        return datetime.fromisoformat(data['datum_prometa'].replace('Z', podesavanja.TIMEZONE))


def get_invoice_item_from_dict(data: dict, magacin_id: int) -> FakturaStavka:
    invoice_item = FakturaStavka()

    invoice_item.sifra = data['sifra']
    invoice_item.naziv = data['naziv']
    invoice_item.izvor_kalkulacije = data['izvor_kalkulacije']

    invoice_item.jedinicna_cijena_osnovna = Decimal(data['jedinicna_cijena_osnovna'])
    invoice_item.jedinicna_cijena_rabatisana = Decimal(data['jedinicna_cijena_rabatisana'])
    invoice_item.jedinicna_cijena_puna = Decimal(data['jedinicna_cijena_puna'])
    invoice_item.jedinicna_cijena_prodajna = Decimal(data['jedinicna_cijena_prodajna'])

    invoice_item.porez_procenat = data.get('porez_procenat')
    invoice_item.rabat_procenat = Decimal(data['rabat_procenat'])

    invoice_item.kolicina = Decimal(data['kolicina'])

    invoice_item.ukupna_cijena_osnovna = Decimal(data['ukupna_cijena_osnovna'])
    invoice_item.ukupna_cijena_rabatisana = Decimal(data['ukupna_cijena_rabatisana'])
    invoice_item.ukupna_cijena_puna = Decimal(data['ukupna_cijena_puna'])
    invoice_item.ukupna_cijena_prodajna = Decimal(data['ukupna_cijena_prodajna'])
    invoice_item.porez_iznos = Decimal(data['porez_iznos'])
    invoice_item.rabat_iznos_osnovni = Decimal(data['rabat_iznos_osnovni'])
    invoice_item.rabat_iznos_prodajni = Decimal(data['rabat_iznos_prodajni'])
    invoice_item.tax_exemption_amount = Decimal(data.get('tax_exemption_amount'))

    invoice_item.credit_note_turnover_used = Decimal(0)
    invoice_item.credit_note_turnover_remaining = Decimal(data['ukupna_cijena_prodajna'])

    invoice_item.jedinica_mjere = db.session.query(JedinicaMjere).get(data['jedinica_mjere_id'])
    invoice_item.tax_exemption_reason_id = data.get('tax_exemption_reason_id')

    magacin_zaliha_id = data.get('magacin_zaliha_id')

    if magacin_zaliha_id:
        magacin_zaliha = db.session.query(MagacinZaliha) \
            .filter(MagacinZaliha.magacin_id == magacin_id) \
            .filter(MagacinZaliha.id == magacin_zaliha_id) \
            .one()

        if magacin_zaliha is None:
            raise ValueError('Stavka zalihe nije pronađena: magacin_zaliha_id=%s ' % magacin_zaliha_id)

        invoice_item.magacin_zaliha = magacin_zaliha

    return invoice_item


def update_corrected_prices_from_current(invoice_item: FakturaStavka, data: dict):
    invoice_item.korigovana_jedinicna_cijena_osnovna = Decimal(data['jedinicna_cijena_osnovna'])
    invoice_item.korigovana_jedinicna_cijena_rabatisana = Decimal(data['jedinicna_cijena_rabatisana'])
    invoice_item.korigovana_jedinicna_cijena_puna = Decimal(data['jedinicna_cijena_puna'])
    invoice_item.korigovana_jedinicna_cijena_prodajna = Decimal(data['jedinicna_cijena_prodajna'])

    invoice_item.korigovana_kolicina = Decimal(data['kolicina'])
    invoice_item.korigovana_ukupna_cijena_osnovna = Decimal(data['ukupna_cijena_osnovna'])
    invoice_item.korigovana_ukupna_cijena_rabatisana = Decimal(data['ukupna_cijena_rabatisana'])
    invoice_item.korigovana_ukupna_cijena_puna = Decimal(data['ukupna_cijena_puna'])
    invoice_item.korigovana_ukupna_cijena_prodajna = Decimal(data['ukupna_cijena_prodajna'])
    invoice_item.korigovani_porez_iznos = Decimal(data['porez_iznos'])
    invoice_item.korigovani_rabat_iznos_osnovni = Decimal(data['rabat_iznos_osnovni'])
    invoice_item.korigovani_rabat_iznos_prodajni = Decimal(data['rabat_iznos_prodajni'])
    invoice_item.corrected_tax_exemption_amount = Decimal(data.get('tax_exemption_amount'))


def get_tax_group_from_dict(data: dict) -> FakturaGrupaPoreza:
    tax_group = FakturaGrupaPoreza()
    tax_group.broj_stavki = data['broj_stavki']
    tax_group.ukupna_cijena_osnovna = data['ukupna_cijena_osnovna']
    tax_group.ukupna_cijena_rabatisana = data['ukupna_cijena_rabatisana']
    tax_group.ukupna_cijena_puna = data['ukupna_cijena_puna']
    tax_group.ukupna_cijena_prodajna = data['ukupna_cijena_prodajna']
    tax_group.porez_procenat = data['porez_procenat']
    tax_group.porez_iznos = data['porez_iznos']
    tax_group.rabat_iznos_osnovni = data['rabat_iznos_osnovni']
    tax_group.rabat_iznos_prodajni = data['rabat_iznos_prodajni']
    tax_group.credit_note_turnover_used = 0
    tax_group.credit_note_turnover_remaining = data['ukupna_cijena_prodajna']

    tax_exemption_reason_id = data['tax_exemption_reason_id']
    if tax_exemption_reason_id is not None:
        tax_group.tax_exemption_reason_id = tax_exemption_reason_id
        tax_group.tax_exemption_reason = get_tax_exemption_reason(tax_exemption_reason_id)
        if tax_group.tax_exemption_reason is None:
            raise InvoiceProcessingException(
                messages={
                    i18n.LOCALE_SR_LATN_ME: 'Pogrešan razlog oslobođenja od poreza.',
                    i18n.LOCALE_EN_US: 'Bad tax exemption reason.'
                })
        tax_group.tax_exemption_amount = data['tax_exemption_amount']
    else:
        tax_group.tax_exemption_reason_id = None
        tax_group.tax_exemption_reason = None
        tax_group.tax_exemption_amount = 0

    return tax_group


def get_tax_exemption_reason(reason_id: int) -> t.Optional[TaxExemptionReason]:
    return db.session.query(TaxExemptionReason) \
        .filter(TaxExemptionReason.id == reason_id) \
        .filter(TaxExemptionReason.is_active.is_(True)) \
        .first()


def get_regular_invoice(invoice_data, firma, operater, naplatni_uredjaj, calculate_totals, calculate_tax_groups):
    invoice = get_invoice_from_dict(
        invoice_data, firma, operater, naplatni_uredjaj, calculate_totals, calculate_tax_groups)

    invoice.tip_fakture_id = Faktura.TYPE_REGULAR
    invoice.customer_invoice_view = enums.CustomerInvoiceView.REGULAR_INVOICES.value

    return invoice

def get_order_invoice(invoice_data, firma, operater, naplatni_uredjaj, calculate_totals, calculate_tax_groups):
    invoice = get_invoice_from_dict(
        invoice_data, firma, operater, naplatni_uredjaj, calculate_totals, calculate_tax_groups)

    invoice.tip_fakture_id = Faktura.TYPE_ORDER
    invoice.customer_invoice_view = enums.CustomerInvoiceView.ORDER_INVOICES.value

    return invoice


def get_final_invoice(invoice_data, firma, opreater, naplatni_uredjaj, advance_invoice_id, calculate_totals,
                      calculate_tax_groups):
    invoice = get_regular_invoice(
        invoice_data, firma, opreater, naplatni_uredjaj, calculate_totals, calculate_tax_groups)

    invoice.advance_invoice_id = advance_invoice_id

    return invoice


def get_advance_invoice(
        invoice_data, firma, opreater, naplatni_uredjaj, calculate_totals=True, calculate_tax_groups=True):

    invoice = get_invoice_from_dict(
        invoice_data, firma, opreater, naplatni_uredjaj, calculate_totals, calculate_tax_groups)

    invoice.tip_fakture_id = Faktura.TYPE_ADVANCE
    invoice.customer_invoice_view = enums.CustomerInvoiceView.ADVANCE_INVOICES.value

    return invoice


def get_invoice_from_dict(
        invoice_data: dict,
        firma: Firma,
        operater: Operater,
        naplatni_uredjaj: NaplatniUredjaj,
        calculate_totals: bool = True,
        calculate_tax_groups: bool = True
) -> Faktura:
    faktura = Faktura()
    faktura.is_cash = invoice_data['is_cash']
    faktura.operater = operater
    faktura.datumvalute = datetime.fromisoformat(invoice_data['datumvalute'].replace('Z', podesavanja.TIMEZONE))
    faktura.poreski_period = datetime.fromisoformat(invoice_data['poreski_period'].replace('Z', podesavanja.TIMEZONE))
    faktura.poreski_period.replace(hour=0, minute=0, second=0, microsecond=0)
    faktura.firma = firma
    faktura.firma_id = firma.id
    faktura.naplatni_uredjaj_id = naplatni_uredjaj.id
    faktura.naplatni_uredjaj = naplatni_uredjaj
    faktura.status = Faktura.STATUS_STORED
    faktura.napomena = invoice_data.get('napomena')
    faktura.valuta_id = invoice_data.get('valuta_id')
    faktura.valuta = get_currency_from_dict(invoice_data)
    faktura.kurs_razmjene = invoice_data['kurs_razmjene']

    faktura.komitent_id = invoice_data.get('komitent_id')
    
    #TODO: Uncomment this later
    #if not faktura.is_cash and faktura.komitent_id is None:
    #    raise InvoiceProcessingException({
    #        i18n.LOCALE_SR_LATN_ME: 'Kupac mora biti definisan kod bezgotovinskih računa.',
    #        i18n.LOCALE_EN_US: 'Kupac mora biti definisan kod bezgotovinskih računa.'
    #    })

    if faktura.komitent_id is not None:
        faktura.komitent = get_buyer_by_id(firma, faktura.komitent_id)

    faktura.datum_prometa = get_datum_prometa_from_dict(invoice_data)

    for _child_invoice_data in invoice_data.get('fakture_djeca', []):
        child_invoice_obj = listaj_fakturu_po_idu(_child_invoice_data['id'])
        if child_invoice_obj is None or child_invoice_obj.firma_id != firma.id:
            raise InvoiceProcessingException(
                messages={
                    i18n.LOCALE_SR_LATN_ME: "Vezana faktura nije pronađena.",
                    i18n.LOCALE_EN_US: "Child invoice is invalid.",
                }
            )
        faktura.fakture_djeca.append(child_invoice_obj)

    for stavka in invoice_data['stavke']:
        invoice_item = get_invoice_item_from_dict(stavka, operater.magacin_id)
        update_corrected_prices_from_current(invoice_item, stavka)
        faktura.stavke.append(invoice_item)

    if calculate_totals:
        update_invoice_totals_from_items(faktura, faktura.stavke)
    else:
        update_invoice_totals_from_dict(faktura, invoice_data)

    faktura.credit_note_turnover_remaining = faktura.ukupna_cijena_prodajna
    faktura.credit_note_turnover_used = 0

    faktura.korigovana_ukupna_cijena_osnovna = faktura.ukupna_cijena_osnovna
    faktura.korigovana_ukupna_cijena_rabatisana = faktura.ukupna_cijena_rabatisana
    faktura.korigovana_ukupna_cijena_puna = faktura.ukupna_cijena_puna
    faktura.korigovana_ukupna_cijena_prodajna = faktura.ukupna_cijena_prodajna
    faktura.korigovani_porez_iznos = faktura.porez_iznos
    faktura.korigovani_rabat_iznos_osnovni = faktura.rabat_iznos_osnovni
    faktura.korigovani_rabat_iznos_prodajni = faktura.rabat_iznos_prodajni
    faktura.corrected_tax_exemption_amount = faktura.tax_exemption_amount

    for payment_method in get_payment_methods_from_dict(invoice_data):
        faktura.payment_methods.append(payment_method)

    if len(faktura.payment_methods) == 1:
        faktura.payment_methods[0].amount = faktura.ukupna_cijena_prodajna

    if calculate_tax_groups:
        for tax_group in get_tax_groups_from_items(faktura):
            faktura.grupe_poreza.append(tax_group)
    else:
        for tax_group_data in invoice_data['grupe_poreza']:
            tax_group = get_tax_group_from_dict(tax_group_data)
            faktura.grupe_poreza.append(tax_group)

    return faktura


def get_corrective_invoice_from_dict(invoice_data: dict) -> Faktura:
    faktura = Faktura()
    faktura.is_cash = invoice_data['is_cash']
    faktura.operater = invoice_data['operater']
    faktura.operater_id = invoice_data['operater_id']
    faktura.datumvalute = invoice_data['datumvalute']
    faktura.poreski_period = invoice_data['poreski_period']
    faktura.firma = invoice_data['firma']
    faktura.firma_id = invoice_data['firma_id']
    faktura.naplatni_uredjaj = invoice_data['naplatni_uredjaj']
    faktura.naplatni_uredjaj_id = invoice_data['naplatni_uredjaj_id']
    faktura.status = Faktura.STATUS_STORED
    faktura.napomena = invoice_data.get('napomena')
    faktura.valuta_id = invoice_data.get('valuta_id')
    faktura.valuta = invoice_data['valuta']
    faktura.valuta_id = invoice_data['valuta_id']
    faktura.kurs_razmjene = invoice_data['kurs_razmjene']
    faktura.tip_fakture_id = invoice_data['tip_fakture_id']
    faktura.komitent_id = invoice_data.get('komitent_id')
    faktura.komitent = invoice_data.get('komitent')
    faktura.datum_prometa = invoice_data.get('datum_prometa')

    set_corrected_invoice_reference(invoice_data, faktura)

    for stavka in invoice_data['stavke']:
        invoice_item = get_invoice_item_from_dict(stavka, faktura.operater.magacin_id)
        update_corrected_prices_from_current(invoice_item, stavka)
        faktura.stavke.append(invoice_item)

    update_invoice_totals_from_items(faktura, faktura.stavke)

    faktura.credit_note_turnover_remaining = faktura.ukupna_cijena_prodajna
    faktura.credit_note_turnover_used = 0
    faktura.korigovana_ukupna_cijena_osnovna = faktura.ukupna_cijena_osnovna
    faktura.korigovana_ukupna_cijena_rabatisana = faktura.ukupna_cijena_rabatisana
    faktura.korigovana_ukupna_cijena_puna = faktura.ukupna_cijena_puna
    faktura.korigovana_ukupna_cijena_prodajna = faktura.ukupna_cijena_prodajna
    faktura.korigovani_porez_iznos = faktura.porez_iznos
    faktura.korigovani_rabat_iznos_osnovni = faktura.rabat_iznos_osnovni
    faktura.korigovani_rabat_iznos_prodajni = faktura.rabat_iznos_prodajni
    faktura.corrected_tax_exemption_amount = faktura.tax_exemption_amount

    for payment_method in get_payment_methods_from_dict(invoice_data):
        faktura.payment_methods.append(payment_method)

    if len(faktura.payment_methods) == 1:
        faktura.payment_methods[0].amount = faktura.ukupna_cijena_prodajna

    for tax_group in get_tax_groups_from_items(faktura):
        faktura.grupe_poreza.append(tax_group)

    return faktura


def deactivate_invoice_schedules(invoice_id):
    db.session.query(InvoiceSchedule) \
        .filter(InvoiceSchedule.source_invoice_id == invoice_id) \
        .update({'is_active': False})


def create_invoice_from_schedule(invoice_schedule: InvoiceSchedule, run_datetime: datetime):
    source_invoice = invoice_schedule.source_invoice

    new_invoice = Faktura()
    new_invoice.source_invoice_id = source_invoice.id
    new_invoice.source_invoice = source_invoice
    new_invoice.is_cash = source_invoice.is_cash
    new_invoice.tip_fakture_id = source_invoice.tip_fakture_id
    new_invoice.operater = invoice_schedule.operater
    new_invoice.operater_id = invoice_schedule.operater.id
    new_invoice.datumvalute = run_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

    new_invoice.poreski_period = datetime.now(pytz.timezone('Europe/Podgorica'))
    new_invoice.poreski_period.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    new_invoice.firma = source_invoice.firma
    new_invoice.naplatni_uredjaj_id = source_invoice.naplatni_uredjaj_id
    new_invoice.naplatni_uredjaj = source_invoice.naplatni_uredjaj
    new_invoice.status = Faktura.STATUS_STORED
    new_invoice.napomena = source_invoice.napomena
    new_invoice.valuta = source_invoice.valuta
    new_invoice.kurs_razmjene = source_invoice.kurs_razmjene
    new_invoice.komitent_id = source_invoice.komitent_id
    new_invoice.komitent = source_invoice.komitent

    for source_payment_method in source_invoice.payment_methods:
        new_payment_method = PaymentMethod()
        new_payment_method.amount = source_payment_method.amount
        new_payment_method.advance_invoice_id = source_payment_method.advance_invoice_id
        new_invoice.payment_methods.append(new_payment_method)

    new_invoice.datum_prometa = source_invoice.datum_prometa  # TODO

    for source_invoice_item in source_invoice.stavke:
        new_invoice_item = FakturaStavka()
        new_invoice_item.sifra = source_invoice_item.sifra
        new_invoice_item.naziv = source_invoice_item.naziv
        new_invoice_item.izvor_kalkulacije = source_invoice_item.izvor_kalkulacije
        new_invoice_item.kolicina = source_invoice_item.kolicina
        new_invoice_item.jedinicna_cijena_osnovna = source_invoice_item.jedinicna_cijena_osnovna
        new_invoice_item.jedinicna_cijena_rabatisana = source_invoice_item.jedinicna_cijena_rabatisana
        new_invoice_item.jedinicna_cijena_puna = source_invoice_item.jedinicna_cijena_puna
        new_invoice_item.jedinicna_cijena_prodajna = source_invoice_item.jedinicna_cijena_prodajna
        new_invoice_item.porez_procenat = source_invoice_item.porez_procenat
        new_invoice_item.rabat_procenat = source_invoice_item.rabat_procenat
        new_invoice_item.korigovana_kolicina = source_invoice_item.korigovana_kolicina
        new_invoice_item.ukupna_cijena_osnovna = source_invoice_item.ukupna_cijena_osnovna
        new_invoice_item.ukupna_cijena_rabatisana = source_invoice_item.ukupna_cijena_rabatisana
        new_invoice_item.ukupna_cijena_puna = source_invoice_item.ukupna_cijena_puna
        new_invoice_item.ukupna_cijena_prodajna = source_invoice_item.ukupna_cijena_prodajna
        new_invoice_item.porez_iznos = source_invoice_item.porez_iznos
        new_invoice_item.rabat_iznos_osnovni = source_invoice_item.rabat_iznos_osnovni
        new_invoice_item.rabat_iznos_prodajni = source_invoice_item.rabat_iznos_prodajni
        new_invoice_item.korigovana_ukupna_cijena_osnovna = source_invoice_item.korigovana_ukupna_cijena_osnovna
        new_invoice_item.korigovana_ukupna_cijena_rabatisana = source_invoice_item.korigovana_ukupna_cijena_rabatisana
        new_invoice_item.korigovana_ukupna_cijena_puna = source_invoice_item.korigovana_ukupna_cijena_puna
        new_invoice_item.korigovana_ukupna_cijena_prodajna = source_invoice_item.korigovana_ukupna_cijena_prodajna
        new_invoice_item.korigovani_porez_iznos = source_invoice_item.korigovani_porez_iznos
        new_invoice_item.korigovani_rabat_iznos_osnovni = source_invoice_item.korigovani_rabat_iznos_osnovni
        new_invoice_item.korigovani_rabat_iznos_prodajni = source_invoice_item.korigovani_rabat_iznos_prodajni
        new_invoice_item.credit_note_turnover_used = 0
        new_invoice_item.credit_note_turnover_remaining = source_invoice_item.korigovana_ukupna_cijena_prodajna
        new_invoice_item.jedinica_mjere = source_invoice_item.jedinica_mjere
        new_invoice_item.tax_exemption_reason_id = source_invoice_item.tax_exemption_reason_id
        new_invoice_item.magacin_zaliha_id = source_invoice_item.magacin_zaliha_id
        new_invoice_item.magacin_zaliha = source_invoice_item.magacin_zaliha

        new_invoice.stavke.append(new_invoice_item)

    new_invoice.ukupna_cijena_osnovna = source_invoice.ukupna_cijena_osnovna
    new_invoice.ukupna_cijena_rabatisana = source_invoice.ukupna_cijena_rabatisana
    new_invoice.ukupna_cijena_puna = source_invoice.ukupna_cijena_puna
    new_invoice.ukupna_cijena_prodajna = source_invoice.ukupna_cijena_prodajna
    new_invoice.porez_iznos = source_invoice.porez_iznos
    new_invoice.rabat_iznos_osnovni = source_invoice.rabat_iznos_osnovni
    new_invoice.rabat_iznos_prodajni = source_invoice.rabat_iznos_prodajni

    new_invoice.korigovana_ukupna_cijena_osnovna = source_invoice.ukupna_cijena_osnovna
    new_invoice.korigovana_ukupna_cijena_rabatisana = source_invoice.ukupna_cijena_rabatisana
    new_invoice.korigovana_ukupna_cijena_puna = source_invoice.ukupna_cijena_puna
    new_invoice.korigovana_ukupna_cijena_prodajna = source_invoice.ukupna_cijena_prodajna
    new_invoice.korigovani_porez_iznos = source_invoice.porez_iznos
    new_invoice.korigovani_rabat_iznos_osnovni = source_invoice.rabat_iznos_osnovni
    new_invoice.korigovani_rabat_iznos_prodajni = source_invoice.rabat_iznos_prodajni

    for source_sametax_item in source_invoice.grupe_poreza:
        new_sametax_item = FakturaGrupaPoreza()
        new_sametax_item.broj_stavki = source_sametax_item.broj_stavki
        new_sametax_item.ukupna_cijena_osnovna = source_sametax_item.ukupna_cijena_osnovna
        new_sametax_item.ukupna_cijena_rabatisana = source_sametax_item.ukupna_cijena_rabatisana
        new_sametax_item.ukupna_cijena_puna = source_sametax_item.ukupna_cijena_puna
        new_sametax_item.ukupna_cijena_prodajna = source_sametax_item.ukupna_cijena_prodajna
        new_sametax_item.porez_procenat = source_sametax_item.porez_procenat
        new_sametax_item.porez_iznos = source_sametax_item.porez_iznos
        new_sametax_item.rabat_iznos_osnovni = source_sametax_item.rabat_iznos_osnovni
        new_sametax_item.rabat_iznos_prodajni = source_sametax_item.rabat_iznos_prodajni
        new_sametax_item.credit_note_turnover_used = 0
        new_sametax_item.credit_note_turnover_remaining = source_sametax_item.credit_note_turnover_remaining
        new_invoice.grupe_poreza.append(new_sametax_item)

    db.session.add(new_invoice)
    db.session.commit()

    return new_invoice


def fiscalize_invoice(faktura: Faktura, fiscalisation_date) -> Faktura:
    _needs_and_has_cash_deposit_or_raise(faktura)

    faktura.uuid = str(uuid_gen.uuid4())
    faktura.datumfakture = fiscalisation_date

    counter_session = db.create_session()
    if fiscalisation_date.year == 2024:
        faktura.internal_ordinal_number = get_internal_ordinal_number(faktura, fiscalisation_date.year, counter_session)
        faktura.efi_ordinal_number = get_efi_ordinal_number(faktura, fiscalisation_date.year, counter_session)
    else:
        ordinal_number = get_internal_ordinal_number(faktura, fiscalisation_date.year, counter_session)
        faktura.internal_ordinal_number = ordinal_number
        faktura.efi_ordinal_number = ordinal_number

    faktura.efi_broj_fakture = '%s/%s/%s/%s' % (
        faktura.naplatni_uredjaj.organizaciona_jedinica.efi_kod,
        faktura.efi_ordinal_number,
        faktura.datumfakture.year,
        faktura.naplatni_uredjaj.efi_kod
    )

    _xml_request = _get_xml_request_or_raise(faktura)

    try:
        posalji_fakturu(faktura, _xml_request)
    except (Exception, InvoiceProcessingException):
        counter_session.rollback()
        raise

    if faktura.jikr is None:
        counter_session.rollback()
        odgovor = listaj_efi_odgovor(faktura.id)

        raise InvoiceProcessingException(
            invoice=faktura,
            messages={
                i18n.LOCALE_SR_LATN_ME: efi_xml.xml_error_to_string(odgovor.faultcode),
                i18n.LOCALE_EN_US: efi_xml.xml_error_to_string(odgovor.faultcode, lang=i18n.LOCALE_EN_US),
            })

    counter_session.commit()

    return faktura



def update_inventory_from_invoice(invoice: Faktura):
    session = db.create_session()

    try:
        for stavka in invoice.stavke:
            if stavka.magacin_zaliha is None:
                continue

            magacin_zaliha = session.query(MagacinZaliha) \
                .with_for_update() \
                .get(stavka.magacin_zaliha_id)

            artikal = session.query(Artikal) \
                .with_for_update() \
                .get(magacin_zaliha.artikal_id)

            if invoice.tip_fakture_id == Faktura.TYPE_REGULAR:
                magacin_zaliha.raspoloziva_kolicina += Decimal(-1) * stavka.kolicina
            elif invoice.tip_fakture_id == Faktura.TYPE_CORRECTIVE:
                if stavka.correction_type_id != InvoiceItemCorrectionType.TYPE_QUANTITY:
                    continue
                magacin_zaliha.raspoloziva_kolicina += Decimal(-1) * stavka.kolicina
            elif invoice.tip_fakture_id == Faktura.TYPE_CANCELLATION:
                if stavka.correction_type_id != InvoiceItemCorrectionType.TYPE_QUANTITY:
                    continue
                magacin_zaliha.raspoloziva_kolicina += Decimal(-1) * stavka.kolicina
            else:
                raise InvoiceProcessingException(
                    messages={
                        i18n.LOCALE_SR_LATN_ME: 'Izmjena inventara nije primjenjiva za tip fakture %s'
                                                % invoice.tip_fakture.naziv,
                        i18n.LOCALE_EN_US: 'Inventory change is not applicable for invoice type %s.'
                                           % invoice.tip_fakture.naziv
                    }
                )

            session.add(magacin_zaliha)
            session.add(artikal)

        session.commit()
        invoice.completed_inventory_update = True
    except (Exception, ):
        session.rollback()
        invoice.completed_inventory_update = False


def _update_cummulative_invoice_from_original(invoice, original):
    invoice.firma = original.firma
    invoice.komitent = original.komitent
    invoice.vrstaplacanja = original.vrstaplacanja
    invoice.datumvalute = original.datumvalute
    invoice.naplatni_uredjaj = original.naplatni_uredjaj
    invoice.valuta = original.valuta
    invoice.kurs_razmjene = original.kurs_razmjene


def _update_corrective_invoice_from_original(invoice, original):
    invoice.korigovana_faktura = original
    invoice.firma = original.firma
    invoice.komitent = original.komitent
    invoice.datumvalute = original.datumvalute
    invoice.naplatni_uredjaj = original.naplatni_uredjaj
    invoice.valuta = original.valuta
    invoice.kurs_razmjene = original.kurs_razmjene
    invoice.is_cash = original.is_cash


def _update_corrective_invoice_item_from_original(item: FakturaStavka, original: FakturaStavka):
    item.sifra = original.sifra
    item.naziv = original.naziv
    item.izvor_kalkulacije = original.izvor_kalkulacije
    item.jedinicna_cijena_osnovna = original.jedinicna_cijena_osnovna
    item.jedinicna_cijena_rabatisana = original.jedinicna_cijena_rabatisana
    item.jedinicna_cijena_puna = original.jedinicna_cijena_puna
    item.jedinicna_cijena_prodajna = original.jedinicna_cijena_prodajna
    item.porez_procenat = original.porez_procenat
    item.rabat_procenat = original.rabat_procenat
    item.jedinica_mjere = original.jedinica_mjere
    item.tax_exemption_reason = original.tax_exemption_reason
    item.tax_exemption_reason_id = original.tax_exemption_reason_id
    item.magacin_zaliha = original.magacin_zaliha


def _update_corrective_invoice_item_from_corrected_dict(item, original, data):
    new_kolicina = Decimal(data['kolicina'])
    new_ukupna_cijena_osnovna = Decimal(data['ukupna_cijena_osnovna'])
    new_ukupna_cijena_rabatisana = Decimal(data['ukupna_cijena_rabatisana'])
    new_ukupna_cijena_puna = Decimal(data['ukupna_cijena_puna'])
    new_porez_iznos = Decimal(data['porez_iznos'])
    new_rabat_iznos_osnovni = Decimal(data['rabat_iznos_osnovni'])
    new_rabat_iznos_prodajni = Decimal(data['rabat_iznos_prodajni'])
    new_ukupna_cijena_prodajna = Decimal(data['ukupna_cijena_prodajna'])
    new_tax_exemption_amount = Decimal(data['tax_exemption_amount'])

    item.kolicina = new_kolicina - original.korigovana_kolicina
    item.corrected_invoice_item_id = original.id
    item.ukupna_cijena_osnovna = new_ukupna_cijena_osnovna - original.korigovana_ukupna_cijena_osnovna
    item.ukupna_cijena_rabatisana = new_ukupna_cijena_rabatisana - original.korigovana_ukupna_cijena_rabatisana
    item.ukupna_cijena_puna = new_ukupna_cijena_puna - original.korigovana_ukupna_cijena_puna
    item.ukupna_cijena_prodajna = new_ukupna_cijena_prodajna - original.korigovana_ukupna_cijena_prodajna
    item.porez_iznos = new_porez_iznos - original.korigovani_porez_iznos
    item.rabat_iznos_osnovni = new_rabat_iznos_osnovni - original.korigovani_rabat_iznos_osnovni
    item.rabat_iznos_prodajni = new_rabat_iznos_prodajni - original.korigovani_rabat_iznos_prodajni
    item.credit_note_turnover_used = 0
    item.credit_note_turnover_remaining = new_ukupna_cijena_prodajna - original.korigovana_ukupna_cijena_prodajna
    item.tax_exemption_amount = new_tax_exemption_amount - original.tax_exemption_amount


def get_corrective_invoice(
        corrected_invoice_data,
        corrective_invoice_data,
        faktura_za_korekciju,
        operater,
        fiscalization_date,
        calculate_totals
):
    korektivna_faktura = Faktura()
    korektivna_faktura.tip_fakture_id = Faktura.TYPE_CORRECTIVE
    korektivna_faktura.poreski_period = datetime.now(pytz.timezone('Europe/Podgorica'))
    korektivna_faktura.poreski_period.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    korektivna_faktura.operater = operater
    korektivna_faktura.status = Faktura.STATUS_STORED
    korektivna_faktura.datumfakture = fiscalization_date

    if faktura_za_korekciju.tip_fakture_id == Faktura.TYPE_REGULAR:
        korektivna_faktura.customer_invoice_view = enums.CustomerInvoiceView.REGULAR_INVOICES.value
    elif faktura_za_korekciju.tip_fakture_id == Faktura.TYPE_ADVANCE:
        korektivna_faktura.customer_invoice_view = enums.CustomerInvoiceView.ADVANCE_INVOICES.value
    else:
        raise Exception('Incorrect value for invoice view.')

    _update_corrective_invoice_from_original(korektivna_faktura, faktura_za_korekciju)

    if len(faktura_za_korekciju.stavke) != len(corrected_invoice_data['stavke']):
        raise InvoiceProcessingException(
            invoice=korektivna_faktura,
            messages={
                i18n.LOCALE_SR_LATN_ME:
                    efi_xml.xml_error_to_string(
                        'Faktura za korekciju i korektivna faktura moraju imati isti broj stavki.'),
                i18n.LOCALE_EN_US:
                    efi_xml.xml_error_to_string(
                        'The corrected invoice and corrective invoice must have the same number of items',
                        lang=i18n.LOCALE_EN_US),
            }
        )

    # for ii in range(len(faktura_za_korekciju.stavke)):
    #     corrective_invoice_item = FakturaStavka()
    #     _update_corrective_invoice_item_from_original(
    #         item=corrective_invoice_item,
    #         original=faktura_za_korekciju.stavke[ii])
    #     _update_corrective_invoice_item_from_corrected_dict(
    #         item=corrective_invoice_item,
    #         original=faktura_za_korekciju.stavke[ii],
    #         data=corrected_invoice_data['stavke'][ii])
    #     korektivna_faktura.stavke.append(corrective_invoice_item)

    for stavka in corrective_invoice_data['stavke']:
        invoice_item = get_invoice_item_from_dict(stavka, operater.magacin_id)
        invoice_item.correction_type_id = stavka['correction_type_id']
        invoice_item.corrected_invoice_item_id = stavka['corrected_invoice_item_id']
        korektivna_faktura.stavke.append(invoice_item)

    grupe_poreza = get_tax_groups_from_items(korektivna_faktura)
    for grupa_poreza in grupe_poreza:
        korektivna_faktura.grupe_poreza.append(grupa_poreza)

    if calculate_totals:
        update_invoice_totals_from_items(korektivna_faktura, korektivna_faktura.stavke)
    else:
        update_corrective_invoice_totals_from_original(korektivna_faktura, faktura_za_korekciju, corrected_invoice_data)

    for new_payment_method in get_payment_methods_from_dict(corrective_invoice_data):
        korektivna_faktura.payment_methods.append(new_payment_method)

    korektivna_faktura.credit_note_turnover_remaining = korektivna_faktura.ukupna_cijena_prodajna
    korektivna_faktura.credit_note_turnover_used = 0

    db.session.add(korektivna_faktura)
    db.session.commit()

    return korektivna_faktura


def make_final_invoice(
        firma, operater, naplatni_uredjaj,
        final_invoice_data, corrected_advance_invoice_data, corrective_for_advance_data,
        calculate_totals=True, calculate_tax_groups=True, fiscalization_date=None, calculate_corrective_totals=True):

    processing = InvoiceProcessing()
    final_invoice = None

    if fiscalization_date is None:
        fiscalization_date = datetime.now(pytz.timezone('Europe/Podgorica'))

    with processing.acquire_lock(naplatni_uredjaj.id) as _:
        final_invoice = get_final_invoice(
            final_invoice_data, firma, operater, naplatni_uredjaj, corrected_advance_invoice_data['id'],
            calculate_totals=calculate_totals, calculate_tax_groups=calculate_tax_groups)

        db.session.add(final_invoice)
        db.session.commit()

        final_invoice = fiscalize_invoice(final_invoice, fiscalization_date)
        update_inventory_from_invoice(final_invoice)
        save_invoice_print(final_invoice)

        advance_invoice = listaj_fakturu_po_idu(corrected_advance_invoice_data['id'])
        corrective_invoice = get_corrective_invoice(
            corrected_advance_invoice_data, corrective_for_advance_data, advance_invoice,
            operater, fiscalization_date, calculate_corrective_totals)
        corrective_invoice = fiscalize_invoice(corrective_invoice, fiscalization_date)
        update_invoice_amounts(corrective_invoice.korigovana_faktura, corrected_advance_invoice_data)
        update_inventory_from_invoice(corrective_invoice)
        save_invoice_print(corrective_invoice)

        db.session.add(corrective_invoice)
        db.session.commit()

        final_invoice.corrective_advance_invoice_id = corrective_invoice.id
        db.session.add(final_invoice)
        db.session.commit()

        corrected_invoice = listaj_fakturu_po_idu(advance_invoice.id)
        _ = create_cummulative_invoice_from_corrected_invoice(corrected_invoice, operater)
        # fiscalised_cummulative_invoice = fiscalize_invoice(cummulative_invoice, fiscalization_date)
        # save_invoice_print(fiscalised_cummulative_invoice)

    return processing, final_invoice


def make_corrective_invoice_from_dict(
        invoice_data: dict,
        naplatni_uredjaj: NaplatniUredjaj
):
    processing = InvoiceProcessing()
    invoice = None

    with processing.acquire_lock(naplatni_uredjaj.id) as _:
        invoice = get_corrective_invoice_from_dict(invoice_data=invoice_data)
        db.session.add(invoice)
        db.session.commit()

        invoice = fiscalize_invoice(invoice, datetime.now())
        update_inventory_from_invoice(invoice)
        save_invoice_print(invoice)

    return processing, invoice


def set_corrected_invoice_reference(invoice_data: dict, invoice: Faktura):
    corrected_invoice_reference = invoice_data['corrected_invoice_reference']
    ref_type = corrected_invoice_reference['type']
    if ref_type == 'invoice':
        invoice.korigovana_faktura = corrected_invoice_reference['invoice']
    elif ref_type == 'credit_note':
        invoice.corrected_credit_note = corrected_invoice_reference['credit_note']
        invoice.customer_invoice_view = enums.CustomerInvoiceView.CREDIT_NOTES.value
    else:
        raise Exception(f'Invalid corrected invoice reference type. Got "{ref_type}".')


def make_regular_invoice(invoice_data, firma, operater, naplatni_uredjaj, calculate_totals=True,
                         calculate_tax_groups=True, fiscalization_date=None):
    processing = InvoiceProcessing()
    invoice = None

    if fiscalization_date is None:
        fiscalization_date = datetime.now(pytz.timezone('Europe/Podgorica'))

    with processing.acquire_lock(naplatni_uredjaj.id) as _:
        invoice = get_regular_invoice(
            invoice_data, firma, operater, naplatni_uredjaj, calculate_totals, calculate_tax_groups)

        db.session.add(invoice)
        db.session.commit()

        invoice = fiscalize_invoice(invoice, fiscalization_date)
        update_inventory_from_invoice(invoice)
        save_invoice_print(invoice)

    return processing, invoice

def make_order_invoice(
        invoice_data: dict,
        firma: Firma,
        operater: Operater,
        naplatni_uredjaj: NaplatniUredjaj,
        calculate_totals: bool = True,
        calculate_tax_groups: bool = True,
        fiscalization_date: datetime = None
):
    invoice_processing = InvoiceProcessing()
    invoice = None

    if fiscalization_date is None:
        fiscalization_date = datetime.now(pytz.timezone('Europe/Podgorica'))

    with invoice_processing.acquire_lock(naplatni_uredjaj.id) as _:
        invoice = get_order_invoice(
            invoice_data, firma, operater, naplatni_uredjaj, calculate_totals, calculate_tax_groups)

        db.session.add(invoice)
        db.session.commit()

        invoice = fiscalize_invoice(invoice, fiscalization_date)

        #Posle uspjesne fiskalizacije, dodajemo fakturu u order_grupa_stavka
        #order_grupa_stavka = OrderGrupaStavka(faktura_id=invoice.id)
        #db.session.add(order_grupa_stavka)
        #db.session.commit()  

        update_inventory_from_invoice(invoice)
        save_invoice_print(invoice)

    return invoice_processing, invoice

def make_advance_invoice(
        invoice_data: dict,
        firma: Firma,
        operater: Operater,
        naplatni_uredjaj: NaplatniUredjaj,
        calculate_totals: bool = True,
        calculate_tax_groups: bool = True,
        fiscalization_date: datetime = None
):
    invoice_processing = InvoiceProcessing()
    invoice = None

    if fiscalization_date is None:
        fiscalization_date = datetime.now(pytz.timezone('Europe/Podgorica'))

    with invoice_processing.acquire_lock(naplatni_uredjaj.id) as _:
        invoice = get_advance_invoice(
            invoice_data, firma, operater, naplatni_uredjaj, calculate_totals, calculate_tax_groups)

        db.session.add(invoice)
        db.session.commit()

        invoice = fiscalize_invoice(invoice, fiscalization_date)
        update_inventory_from_invoice(invoice)
        save_invoice_print(invoice)

    return invoice_processing, invoice


def make_regular_invoice_from_invoice_schedule(invoice_schedule, run_datetime):
    _current_next_run_datetime = invoice_schedule.next_run_datetime

    _new_next_run_datetime = \
        _current_next_run_datetime \
        + relativedelta(months=invoice_schedule.frequency_interval)

    if invoice_schedule.next_run_datetime < run_datetime:
        invoice_schedule.last_run_datetime = _current_next_run_datetime
        invoice_schedule.next_run_datetime = _new_next_run_datetime

    if invoice_schedule.end_datetime is not None and _new_next_run_datetime > invoice_schedule.end_datetime:
        invoice_schedule.is_active = False

    db.session.add(invoice_schedule)
    db.session.commit()

    invoice_processing = InvoiceProcessing()
    invoice = None

    with invoice_processing.acquire_lock(invoice_schedule.source_invoice.naplatni_uredjaj.id) as _:
        invoice = create_invoice_from_schedule(invoice_schedule, run_datetime)

        db.session.add(invoice)
        db.session.commit()

        invoice = fiscalize_invoice(invoice, datetime.now(pytz.timezone('Europe/Podgorica')))
        update_inventory_from_invoice(invoice)
        save_invoice_print(invoice)

    return invoice_processing, invoice


def get_active_invoice_schedules():
    return db.session.query(InvoiceSchedule) \
        .filter(InvoiceSchedule.is_active.is_(True)) \
        .all()


def make_corrective_invoice(
        operater,
        korigovana_faktura,
        corrected_invoice_data,
        corrective_invoice_data,
        fiscalization_date,
        calculate_totals: bool = True
):
    invoice_processing = InvoiceProcessing()

    corrective_invoice = None
    cummulative_invoice = None

    with invoice_processing.acquire_lock(korigovana_faktura.naplatni_uredjaj.id) as _:
        corrective_invoice = get_corrective_invoice(
            corrected_invoice_data, corrective_invoice_data, korigovana_faktura, operater, fiscalization_date,
            calculate_totals)
        corrective_invoice = fiscalize_invoice(corrective_invoice, fiscalization_date)
        update_invoice_amounts(corrective_invoice.korigovana_faktura, corrected_invoice_data)
        update_inventory_from_invoice(corrective_invoice)
        save_invoice_print(corrective_invoice)

        db.session.add(corrective_invoice)
        db.session.commit()

        corrected_invoice = listaj_fakturu_po_idu(korigovana_faktura.id)
        cummulative_invoice = create_cummulative_invoice_from_corrected_invoice(corrected_invoice, operater)
        # fiscalised_cummulative_invoice = fiscalize_invoice(cummulative_invoice, fiscalization_date)
        # save_invoice_print(fiscalised_cummulative_invoice)

    return invoice_processing, corrective_invoice, cummulative_invoice


def save_invoice_print(invoice):
    if podesavanja.EFI_FILES_STORE is None:
        return

    path_a4 = Path(podesavanja.EFI_FILES_STORE, 'faktura_%s__A4.pdf' % invoice.id)
    stampa.save_to_file(invoice, path_a4, 'a4')
    path_58mm = Path(podesavanja.EFI_FILES_STORE, 'faktura_%s__58mm.pdf' % invoice.id)
    stampa.save_to_file(invoice, path_58mm, '58mm')


def update_invoice_amounts(invoice, corrected_invoice_data):
    invoice.korigovana_ukupna_cijena_prodajna = corrected_invoice_data['ukupna_cijena_prodajna']
    invoice.korigovana_ukupna_cijena_osnovna = corrected_invoice_data['ukupna_cijena_osnovna']
    invoice.korigovana_ukupna_cijena_puna = corrected_invoice_data['ukupna_cijena_puna']
    invoice.korigovana_ukupna_cijena_rabatisana = corrected_invoice_data['ukupna_cijena_rabatisana']
    invoice.korigovani_porez_iznos = corrected_invoice_data['porez_iznos']
    invoice.korigovani_rabat_iznos_osnovni = corrected_invoice_data['rabat_iznos_osnovni']
    invoice.korigovani_rabat_iznos_prodajni = corrected_invoice_data['rabat_iznos_prodajni']
    invoice.corrected_tax_exemption_amount = corrected_invoice_data['tax_exemption_amount']
    invoice.credit_note_turnover_remaining = corrected_invoice_data['ukupna_cijena_prodajna']

    for ii in range(len(invoice.stavke)):
        corrected_item = invoice.stavke[ii]
        new_item_amounts = corrected_invoice_data['stavke'][ii]

        corrected_item.korigovana_jedinicna_cijena_osnovna = \
            Decimal(new_item_amounts['jedinicna_cijena_osnovna'])
        corrected_item.korigovana_jedinicna_cijena_rabatisana = \
            Decimal(new_item_amounts['jedinicna_cijena_rabatisana'])
        corrected_item.korigovana_jedinicna_cijena_prodajna = \
            Decimal(new_item_amounts['jedinicna_cijena_prodajna'])
        corrected_item.korigovana_jedinicna_cijena_puna = \
            Decimal(new_item_amounts['jedinicna_cijena_puna'])

        corrected_item.korigovana_kolicina = \
            Decimal(new_item_amounts['kolicina'])
        corrected_item.korigovana_ukupna_cijena_osnovna = \
            Decimal(new_item_amounts['ukupna_cijena_osnovna'])
        corrected_item.korigovana_ukupna_cijena_rabatisana = \
            Decimal(new_item_amounts['ukupna_cijena_rabatisana'])
        corrected_item.korigovana_ukupna_cijena_puna = \
            Decimal(new_item_amounts['ukupna_cijena_puna'])
        corrected_item.korigovana_ukupna_cijena_prodajna = \
            Decimal(new_item_amounts['ukupna_cijena_prodajna'])
        corrected_item.korigovani_porez_iznos = \
            Decimal(new_item_amounts['porez_iznos'])
        corrected_item.korigovani_rabat_iznos_osnovni = \
            Decimal(new_item_amounts['rabat_iznos_osnovni'])
        corrected_item.korigovani_rabat_iznos_prodajni = \
            Decimal(new_item_amounts['rabat_iznos_prodajni'])
        corrected_item.corrected_tax_exemption_amount = \
            Decimal(new_item_amounts['tax_exemption_amount'])
        corrected_item.credit_note_turnover_remaining = \
            Decimal(new_item_amounts['ukupna_cijena_prodajna']) \

    nove_grupe_poreza = get_tax_groups_from_items(invoice)
    for nova_grupa_poreza in nove_grupe_poreza:
        for stara_grupa_poreza in invoice.grupe_poreza:
            if nova_grupa_poreza.porez_procenat == stara_grupa_poreza.porez_procenat:
                stara_grupa_poreza.broj_stavki = nova_grupa_poreza.broj_stavki
                stara_grupa_poreza.porez_procenat = nova_grupa_poreza.porez_procenat
                stara_grupa_poreza.ukupna_cijena_osnovna = nova_grupa_poreza.ukupna_cijena_osnovna
                stara_grupa_poreza.ukupna_cijena_rabatisana = nova_grupa_poreza.ukupna_cijena_rabatisana
                stara_grupa_poreza.ukupna_cijena_puna = nova_grupa_poreza.ukupna_cijena_puna
                stara_grupa_poreza.ukupna_cijena_prodajna = nova_grupa_poreza.ukupna_cijena_prodajna
                stara_grupa_poreza.porez_iznos = nova_grupa_poreza.porez_iznos
                stara_grupa_poreza.rabat_iznos_osnovni = nova_grupa_poreza.rabat_iznos_osnovni
                stara_grupa_poreza.rabat_iznos_prodajni = nova_grupa_poreza.rabat_iznos_prodajni
                stara_grupa_poreza.ukupna_cijena_prodajna = nova_grupa_poreza.ukupna_cijena_prodajna
                stara_grupa_poreza.credit_note_turnover_remaining = nova_grupa_poreza.ukupna_cijena_prodajna
                stara_grupa_poreza.tax_exemption_amount = nova_grupa_poreza.tax_exemption_amount

    db.session.add(invoice)
    db.session.commit()


def create_cummulative_invoice_from_corrected_invoice(korigovana_faktura: Faktura, operater: Operater):
    zbirna_faktura = Faktura()
    zbirna_faktura.tip_fakture_id = Faktura.TYPE_CUMMULATIVE
    zbirna_faktura.poreski_period = datetime.now(pytz.timezone('Europe/Podgorica'))
    zbirna_faktura.poreski_period.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    zbirna_faktura.operater = operater
    zbirna_faktura.status = Faktura.STATUS_STORED

    _update_cummulative_invoice_from_original(zbirna_faktura, korigovana_faktura)

    zbirna_faktura.clanice_zbirne_fakture.append(korigovana_faktura)
    for korektivna_faktura in korigovana_faktura.korektivne_fakture:
        zbirna_faktura.clanice_zbirne_fakture.append(korektivna_faktura)

    for stavka in korigovana_faktura.stavke:
        nova_stavka = FakturaStavka()
        nova_stavka.sifra = stavka.sifra
        nova_stavka.kolicina = stavka.korigovana_kolicina
        nova_stavka.izvor_kalkulacije = stavka.izvor_kalkulacije
        nova_stavka.jedinicna_cijena_osnovna = stavka.jedinicna_cijena_osnovna
        nova_stavka.jedinicna_cijena_rabatisana = stavka.jedinicna_cijena_rabatisana
        nova_stavka.jedinicna_cijena_puna = stavka.jedinicna_cijena_puna
        nova_stavka.jedinicna_cijena_prodajna = stavka.jedinicna_cijena_prodajna
        nova_stavka.porez_procenat = stavka.porez_procenat
        nova_stavka.rabat_procenat = stavka.rabat_procenat
        nova_stavka.ukupna_cijena_osnovna = stavka.korigovana_ukupna_cijena_osnovna
        nova_stavka.ukupna_cijena_rabatisana = stavka.korigovana_ukupna_cijena_rabatisana
        nova_stavka.ukupna_cijena_puna = stavka.korigovana_ukupna_cijena_puna
        nova_stavka.ukupna_cijena_prodajna = stavka.korigovana_ukupna_cijena_prodajna
        nova_stavka.porez_iznos = stavka.korigovani_porez_iznos
        nova_stavka.rabat_iznos_osnovni = stavka.korigovani_rabat_iznos_osnovni
        nova_stavka.rabat_iznos_prodajni = stavka.korigovani_rabat_iznos_prodajni
        nova_stavka.naziv = stavka.naziv
        nova_stavka.credit_note_turnover_used = 0
        nova_stavka.credit_note_turnover_remaining = stavka.korigovani_rabat_iznos_prodajni
        nova_stavka.jedinica_mjere_id = stavka.jedinica_mjere_id
        nova_stavka.tax_exemption_reason_id = stavka.tax_exemption_reason_id
        nova_stavka.magacin_zaliha_id = stavka.magacin_zaliha_id
        nova_stavka.credit_note_turnover_remaining = stavka.ukupna_cijena_prodajna
        nova_stavka.credit_note_turnover_used = 0
        nova_stavka.tax_exemption_amount = stavka.tax_exemption_amount
        nova_stavka.corrected_tax_exemption_amount = stavka.corrected_tax_exemption_amount
        zbirna_faktura.stavke.append(nova_stavka)

    update_invoice_totals_from_items(zbirna_faktura, korigovana_faktura.stavke, use_corrected_amounts=True)

    zbirna_faktura.credit_note_turnover_remaining = zbirna_faktura.ukupna_cijena_prodajna
    zbirna_faktura.credit_note_turnover_used = 0

    payment_method = PaymentMethod()
    payment_method.payment_method_type_id = korigovana_faktura.payment_methods[0].payment_method_type_id
    payment_method.amount = zbirna_faktura.ukupna_cijena_prodajna
    zbirna_faktura.payment_methods.append(payment_method)

    grupe_poreza = formiraj_korigovane_grupe_poreza(korigovana_faktura)
    for grupa_poreza in grupe_poreza:
        zbirna_faktura.grupe_poreza.append(grupa_poreza)

    db.session.add(zbirna_faktura)
    db.session.commit()

    return zbirna_faktura


def make_cancellation_invoice(
    korigovana_faktura: Faktura,
    operater: Operater,
    fiscalization_date: datetime
):
    corrected_invoice_data = {}
    corrected_invoice_data['ukupna_cijena_prodajna'] = 0
    corrected_invoice_data['ukupna_cijena_osnovna'] = 0
    corrected_invoice_data['ukupna_cijena_puna'] = 0
    corrected_invoice_data['ukupna_cijena_rabatisana'] = 0
    corrected_invoice_data['porez_iznos'] = 0
    corrected_invoice_data['rabat_iznos_osnovni'] = 0
    corrected_invoice_data['rabat_iznos_prodajni'] = 0
    corrected_invoice_data['tax_exemption_amount'] = 0

    corrected_invoice_data['stavke'] = []
    for original_invoice_item in korigovana_faktura.stavke:
        corrected_invoice_data['stavke'].append({
            'kolicina': 0,
            'jedinicna_cijena_osnovna': original_invoice_item.korigovana_jedinicna_cijena_osnovna,
            'jedinicna_cijena_rabatisana': original_invoice_item.korigovana_jedinicna_cijena_rabatisana,
            'jedinicna_cijena_puna': original_invoice_item.korigovana_jedinicna_cijena_puna,
            'jedinicna_cijena_prodajna': original_invoice_item.korigovana_jedinicna_cijena_prodajna,
            'ukupna_cijena_osnovna': 0,
            'ukupna_cijena_rabatisana': 0,
            'ukupna_cijena_puna': 0,
            'ukupna_cijena_prodajna': 0,
            'porez_iznos': 0,
            'rabat_iznos_osnovni': 0,
            'rabat_iznos_prodajni': 0,
            'tax_exemption_amount': original_invoice_item.corrected_tax_exemption_amount
        })

    corrective_invoice_data = {}
    corrective_invoice_data['stavke'] = []
    for original_invoice_item in korigovana_faktura.stavke:
        corrective_invoice_data['stavke'].append({
            'sifra': original_invoice_item.sifra,
            'naziv': '%s - korekcija količine' % original_invoice_item.naziv,
            'izvor_kalkulacije': original_invoice_item.izvor_kalkulacije,
            'jedinicna_cijena_osnovna': original_invoice_item.jedinicna_cijena_osnovna,
            'jedinicna_cijena_rabatisana': original_invoice_item.jedinicna_cijena_rabatisana,
            'jedinicna_cijena_puna': original_invoice_item.jedinicna_cijena_puna,
            'jedinicna_cijena_prodajna': original_invoice_item.jedinicna_cijena_prodajna,
            'porez_procenat': original_invoice_item.porez_procenat,
            'rabat_procenat': original_invoice_item.rabat_procenat,
            'kolicina': Decimal(-1) * original_invoice_item.korigovana_kolicina,
            'ukupna_cijena_osnovna': Decimal(-1) * original_invoice_item.korigovana_ukupna_cijena_osnovna,
            'ukupna_cijena_rabatisana': Decimal(-1) * original_invoice_item.korigovana_ukupna_cijena_rabatisana,
            'ukupna_cijena_puna': Decimal(-1) * original_invoice_item.korigovana_ukupna_cijena_puna,
            'ukupna_cijena_prodajna': Decimal(-1) * original_invoice_item.korigovana_ukupna_cijena_prodajna,
            'porez_iznos': Decimal(-1) * original_invoice_item.korigovani_porez_iznos,
            'rabat_iznos_osnovni': Decimal(-1) * original_invoice_item.korigovani_rabat_iznos_osnovni,
            'rabat_iznos_prodajni': Decimal(-1) * original_invoice_item.korigovani_rabat_iznos_prodajni,
            'tax_exemption_amount': original_invoice_item.corrected_tax_exemption_amount,
            'tax_exemption_reason_id': original_invoice_item.tax_exemption_reason_id,
            'tax_exemption_reason': original_invoice_item.tax_exemption_reason,
            'magacin_zaliha': original_invoice_item.magacin_zaliha,
            'magacin_zaliha_id': original_invoice_item.magacin_zaliha_id,
            'jedinica_mjere': original_invoice_item.jedinica_mjere,
            'jedinica_mjere_id': original_invoice_item.jedinica_mjere_id,
            'correction_type_id': InvoiceItemCorrectionType.TYPE_QUANTITY,
            'corrected_invoice_item_id': original_invoice_item.id,
        })

    corrective_invoice_data['payment_methods'] = []
    if len(korigovana_faktura.payment_methods) == 1:
        original_payment_method = korigovana_faktura.payment_methods[0]
        corrective_payment_method = {
            'payment_method_type_id': original_payment_method.payment_method_type_id,
            'payment_method_type': original_payment_method.payment_method_type,
            'amount': -1 * korigovana_faktura.korigovana_ukupna_cijena_prodajna
        }

        corrective_invoice_data['payment_methods'].append(corrective_payment_method)
    else:
        if len(korigovana_faktura.korektivne_fakture) > 0:
            raise InvoiceProcessingException(
                invoice=korigovana_faktura,
                messages={
                    i18n.LOCALE_SR_LATN_ME:
                        'Račun ima korekcije i mora se stornirati ručno putem korekcije računa.',
                    i18n.LOCALE_EN_US:
                        'The invoice has corrections and must be canceled manually via the invoice correction.',
                })

        for original_payment_method in korigovana_faktura.payment_methods:
            corrective_payment_method = {
                'payment_method_type_id': original_payment_method.payment_method_type_id,
                'payment_method_type': original_payment_method.payment_method_type,
                'amount': -1 * original_payment_method.amount
            }

            if original_payment_method.payment_method_type_id == PaymentMethod.TYPE_ADVANCE:
                corrective_payment_method['advance_invoice'] = {
                    'id': original_payment_method.advance_invoice_id
                }
                corrective_payment_method['advance_invoice_id'] = original_payment_method.advance_invoice_id

            corrective_invoice_data['payment_methods'].append(corrective_payment_method)

    return make_corrective_invoice(
        operater, korigovana_faktura, corrected_invoice_data, corrective_invoice_data, fiscalization_date,
        calculate_totals=False)


def posalji_fakturu(faktura: Faktura, xml_request):
    request = RegisterInvoiceRequest()
    request.uuid = str(uuid_gen.uuid4())
    request.faktura = faktura
    db.session.add(request)
    db.session.commit()

    if podesavanja.EFI_FILES_STORE is not None:
        with open(Path(podesavanja.EFI_FILES_STORE, 'faktura_%s__request.xml' % faktura.id), 'wb') as f:
            f.write(xml_request)

    try:
        response = requests.post(
            url=podesavanja.EFI_SERVICE_URL,
            data=xml_request,
            verify=False,
            headers={
                'Content-Type': 'text/xml; charset=utf-8'
            })
    except requests.ConnectionError as connection_error:
        raise InvoiceProcessingException(
            invoice=faktura,
            original_exception=connection_error,
            messages={
                i18n.LOCALE_SR_LATN_ME: 'Došlo je do greške u komunikaciji sa servisom poreske uprave.',
                i18n.LOCALE_EN_US: 'Tax administration office service is unavailable. Please try again later.',
            })
    except Exception as exception:
        raise InvoiceProcessingException(
            invoice=faktura,
            original_exception=exception,
            messages={
                i18n.LOCALE_SR_LATN_ME: "Došlo je do nepoznate greške.",
                i18n.LOCALE_EN_US: 'Unknown error',
            })

    if podesavanja.EFI_FILES_STORE is not None:
        with open(Path(podesavanja.EFI_FILES_STORE, 'faktura_%s__response.xml' % faktura.id), 'wb') as f:
            f.write(response.content)

    response_uuid, faultcode, faultstring, jikr = efi_xml.read_register_invoice_response(response.content.decode())

    register_invoice_response = RegisterInvoiceResponse()
    register_invoice_response.faktura = faktura
    register_invoice_response.uuid = response_uuid
    register_invoice_response.register_invoice_request_id = request.id

    if jikr is not None:
        faktura.jikr = jikr
        faktura.status = Faktura.STATUS_FISCALISATION_SUCCESS
        faktura.efi_verify_url = get_efi_verify_url(faktura, is_long=True)
        db.session.commit()
    else:
        faktura.status = Faktura.STATUS_FISCALISATION_FAIL
        register_invoice_response.faultcode = faultcode
        register_invoice_response.faultstring = faultstring
        db.session.commit()

    request.register_invoice_response = register_invoice_response
    db.session.add(register_invoice_response)
    db.session.commit()

    return faktura


def get_iic_params(invoice: Faktura):
    return "|".join([
        '%s' % invoice.firma.pib,
        '%s' % invoice.datumfakture,
        '%s' % invoice.efi_ordinal_number,
        '%s' % invoice.naplatni_uredjaj.organizaciona_jedinica.efi_kod,
        '%s' % invoice.naplatni_uredjaj.efi_kod,
        '%s' % podesavanja.EFI_KOD_SOFTVERA,
        '%s' % invoice.ukupna_cijena_prodajna
    ]).encode()


def _get_xml_request_or_raise(faktura):
    db_certificate = certificate_opb.get_certificate_by_customer(faktura.firma, faktura.datumfakture)
    if db_certificate is None:
        raise InvoiceProcessingException(
            messages={
                i18n.LOCALE_SR_LATN_ME: 'Nije moguće potpisati račun jer no postoji ispravan sertifikat za potpisavanje za aktuelni period.',
                i18n.LOCALE_EN_US: 'It is not possible to sign the invoice because there is no valid signing certificate for the current period.',
            }
        )

    try:
        private_key, certificate, _ = fiskalizacija.from_certificate_store(db_certificate.fingerprint, db_certificate.password)
    except OpenSSLCryptoError:
        raise InvoiceProcessingException(
            messages={
                i18n.LOCALE_SR_LATN_ME: 'Greška prilikom pristupa sertifikatu za potpisivanje.',
                i18n.LOCALE_EN_US: 'Error while trying to access certificate.',
            }
        )

    iic_digest, iic_signature = fiskalizacija.get_iic_digest_and_signature(get_iic_params(faktura), private_key)
    faktura.iic = iic_digest
    faktura.ikof = iic_digest
    db.session.add(faktura)
    db.session.commit()

    try:
        unsinged_xml = efi_xml.generate_register_invoice_request(faktura, iic_signature)
        unsigned_xml_bytes = efi_xml.tostring(unsinged_xml)
    except Exception as exception:
        logger.exception('Cannot format XML for fiscalization.')
        raise InvoiceProcessingException(
            invoice=faktura,
            original_exception=exception,
            messages={
                i18n.LOCALE_SR_LATN_ME:
                    'Došlo je do greške prilikom formiranja poruke za prijavu računa poreskoj upravi.',
                i18n.LOCALE_EN_US:
                    'Error occurred while formatting message.',
            })

    # TODO Do we need to keep unsinged XML request as file?
    if podesavanja.EFI_FILES_STORE is not None:
        with open(Path(podesavanja.EFI_FILES_STORE, 'faktura_%s__request_unsigned.xml' % faktura.id), 'wb') as f:
            f.write(unsigned_xml_bytes)

    try:
        signed_xml = fiskalizacija.potpisi(unsinged_xml, private_key, certificate)
        signed_xml_bytes = efi_xml.tostring(signed_xml)
    except Exception as exception:
        raise InvoiceProcessingException(
            invoice=faktura,
            original_exception=exception,
            messages={
                i18n.LOCALE_SR_LATN_ME:
                    'Došlo je do greške prilikom potpisivanja poruke za prijavu računa poreskoj upravi.',
                i18n.LOCALE_EN_US:
                    'Error occured while formatting the message.'
            })

    if podesavanja.EFI_FILES_STORE is not None:
        with open(Path(podesavanja.EFI_FILES_STORE, 'faktura_%s__request.xml' % faktura.id), 'wb') as f:
            f.write(signed_xml_bytes)

    return signed_xml_bytes


def create_invoice_template(
        podaci,
        firma,
        operater,
        naplatni_uredjaj,
        calculate_totals=True,
        calculate_tax_groups=True
):
    invoice = get_invoice_from_dict(
        podaci, firma, operater, naplatni_uredjaj, calculate_totals, calculate_tax_groups)
    invoice.tip_fakture_id = Faktura.TYPE_INVOICE_TEMPLATE
    invoice.customer_invoice_view = enums.CustomerInvoiceView.REGULAR_INVOICE_TEMPLATES.value
    invoice.status = Faktura.STATUS_FISCALISATION_SUCCESS
    invoice.datumfakture = datetime.now()

    invoice.internal_ordinal_number = get_next_ordinal_number(
        type_id=enums.OrdinalNumberCounterType.INVOICE_TEMPLATES.value,
        payment_device_id=invoice.naplatni_uredjaj_id,
        year=invoice.datumfakture.year,
        session=db.session
    )
    db.session.add(invoice)
    db.session.commit()

    return invoice


def get_invoice_templates_query(company):
    return db.session.query(Faktura) \
        .filter(Faktura.firma_id == company.id) \
        .filter(Faktura.tip_fakture_id == Faktura.TYPE_INVOICE_TEMPLATE)


def get_invoice_templates(company):
    return get_invoice_templates_query(company).all()


def jedinica_mjere__listaj(firma):
    return db.session.query(JedinicaMjere) \
        .filter(JedinicaMjere.firma_id == firma.id) \
        .all()


def get_payment_method_types():
    return db.session.query(PaymentMethodType) \
        .filter(PaymentMethodType.is_active.is_(True)) \
        .order_by(PaymentMethodType.sort_weight)


def get_tax_groups_from_items(faktura: Faktura) -> t.List[FakturaGrupaPoreza]:
    tax_groups = {}  # Contains tax items
    exemption_groups = {}  # Contains tax exempted items

    for invoice_item in faktura.stavke:
        if invoice_item.tax_exemption_reason_id is None:
            if invoice_item.porez_procenat not in tax_groups:
                tax_group = FakturaGrupaPoreza()
                tax_group.broj_stavki = 0
                tax_group.ukupna_cijena_osnovna = 0
                tax_group.ukupna_cijena_rabatisana = 0
                tax_group.ukupna_cijena_puna = 0
                tax_group.ukupna_cijena_prodajna = 0
                tax_group.porez_procenat = invoice_item.porez_procenat
                tax_group.porez_iznos = 0
                tax_group.rabat_iznos_osnovni = 0
                tax_group.rabat_iznos_prodajni = 0
                tax_group.credit_note_turnover_used = 0
                tax_group.credit_note_turnover_remaining = 0
                tax_group.tax_exemption_reason_id = None
                tax_group.tax_exemption_amount = 0
                tax_groups[invoice_item.porez_procenat] = tax_group

            tax_group = tax_groups[invoice_item.porez_procenat]
        else:
            if invoice_item.tax_exemption_reason_id not in exemption_groups:
                tax_group = FakturaGrupaPoreza()
                tax_group.broj_stavki = 0
                tax_group.ukupna_cijena_osnovna = 0
                tax_group.ukupna_cijena_rabatisana = 0
                tax_group.ukupna_cijena_puna = 0
                tax_group.ukupna_cijena_prodajna = 0
                tax_group.porez_iznos = 0
                tax_group.rabat_iznos_osnovni = 0
                tax_group.rabat_iznos_prodajni = 0
                tax_group.credit_note_turnover_used = 0
                tax_group.credit_note_turnover_remaining = 0
                tax_group.tax_exemption_reason_id = invoice_item.tax_exemption_reason_id
                tax_group.tax_exemption_amount = 0
                exemption_groups[invoice_item.tax_exemption_reason_id] = tax_group

            tax_group = exemption_groups[invoice_item.tax_exemption_reason_id]

        tax_group.broj_stavki += 1
        tax_group.ukupna_cijena_osnovna += invoice_item.ukupna_cijena_osnovna
        tax_group.ukupna_cijena_rabatisana += invoice_item.ukupna_cijena_rabatisana
        tax_group.ukupna_cijena_puna += invoice_item.ukupna_cijena_puna
        tax_group.ukupna_cijena_prodajna += invoice_item.ukupna_cijena_prodajna
        tax_group.porez_iznos += invoice_item.porez_iznos
        tax_group.rabat_iznos_osnovni += invoice_item.rabat_iznos_osnovni
        tax_group.rabat_iznos_prodajni += invoice_item.rabat_iznos_prodajni
        tax_group.credit_note_turnover_used += invoice_item.credit_note_turnover_used
        tax_group.credit_note_turnover_remaining += invoice_item.credit_note_turnover_remaining
        tax_group.tax_exemption_amount += invoice_item.tax_exemption_amount

    return [*tax_groups.values(), *exemption_groups.values()]


def get_active_tax_exemption_reasons():
    return db.session.query(TaxExemptionReason) \
        .filter(TaxExemptionReason.is_active.is_(True)) \
        .all()


def get_tax_exemption_reason_by_id(reason_id: int) -> t.Optional[TaxExemptionReason]:
    return db.session.query(TaxExemptionReason) \
        .filter(TaxExemptionReason.id == reason_id) \
        .filter(TaxExemptionReason.is_active.is_(True)) \
        .first()


def update_corrective_invoice_totals_from_original(invoice: Faktura, original: Faktura, corrected_invoice_data):
    invoice.ukupna_cijena_osnovna = \
        Decimal(corrected_invoice_data['ukupna_cijena_osnovna']) \
        - original.korigovana_ukupna_cijena_osnovna

    invoice.ukupna_cijena_rabatisana = \
        Decimal(corrected_invoice_data['ukupna_cijena_rabatisana']) \
        - original.korigovana_ukupna_cijena_rabatisana

    invoice.ukupna_cijena_puna = \
        Decimal(corrected_invoice_data['ukupna_cijena_puna']) \
        - original.korigovana_ukupna_cijena_puna

    invoice.ukupna_cijena_prodajna = \
        Decimal(corrected_invoice_data['ukupna_cijena_prodajna']) \
        - original.korigovana_ukupna_cijena_prodajna

    invoice.porez_iznos = \
        Decimal(corrected_invoice_data['porez_iznos']) \
        - original.korigovani_porez_iznos

    invoice.rabat_iznos_osnovni = \
        Decimal(corrected_invoice_data['rabat_iznos_osnovni']) \
        - original.korigovani_rabat_iznos_osnovni

    invoice.rabat_iznos_prodajni = \
        Decimal(corrected_invoice_data['rabat_iznos_prodajni']) \
        - original.korigovani_rabat_iznos_prodajni

    invoice.tax_exemption_amount = \
        Decimal(corrected_invoice_data['tax_exemption_amount']) \
        - original.tax_exemption_amount


def update_invoice_totals_from_items(invoice: Faktura, invoice_items: t.List[FakturaStavka],
                                     use_corrected_amounts: bool = False):
    ukupna_cijena_osnovna = Decimal(0)
    ukupna_cijena_rabatisana = Decimal(0)
    ukupna_cijena_puna = Decimal(0)
    ukupna_cijena_prodajna = Decimal(0)
    porez_iznos = Decimal(0)
    rabat_iznos_osnovni = Decimal(0)
    rabat_iznos_prodajni = Decimal(0)
    tax_exemption_amount = Decimal(0)

    if use_corrected_amounts:
        for invoice_item in invoice_items:
            ukupna_cijena_osnovna += invoice_item.korigovana_ukupna_cijena_osnovna
            ukupna_cijena_rabatisana += invoice_item.korigovana_ukupna_cijena_rabatisana
            ukupna_cijena_puna += invoice_item.korigovana_ukupna_cijena_puna
            ukupna_cijena_prodajna += invoice_item.korigovana_ukupna_cijena_prodajna
            porez_iznos += invoice_item.korigovani_porez_iznos
            rabat_iznos_osnovni += invoice_item.korigovani_rabat_iznos_osnovni
            rabat_iznos_prodajni += invoice_item.korigovani_rabat_iznos_prodajni
            tax_exemption_amount += invoice_item.corrected_tax_exemption_amount
    else:
        for invoice_item in invoice_items:
            ukupna_cijena_osnovna += invoice_item.ukupna_cijena_osnovna
            ukupna_cijena_rabatisana += invoice_item.ukupna_cijena_rabatisana
            ukupna_cijena_puna += invoice_item.ukupna_cijena_puna
            ukupna_cijena_prodajna += invoice_item.ukupna_cijena_prodajna
            porez_iznos += invoice_item.porez_iznos
            rabat_iznos_osnovni += invoice_item.rabat_iznos_osnovni
            rabat_iznos_prodajni += invoice_item.rabat_iznos_prodajni
            tax_exemption_amount += invoice_item.tax_exemption_amount

    invoice.ukupna_cijena_osnovna = ukupna_cijena_osnovna
    invoice.ukupna_cijena_rabatisana = ukupna_cijena_rabatisana
    invoice.ukupna_cijena_puna = ukupna_cijena_puna
    invoice.ukupna_cijena_prodajna = ukupna_cijena_prodajna
    invoice.porez_iznos = porez_iznos
    invoice.rabat_iznos_osnovni = rabat_iznos_osnovni
    invoice.rabat_iznos_prodajni = rabat_iznos_prodajni
    invoice.tax_exemption_amount = tax_exemption_amount


def update_invoice_totals_from_dict(invoice: Faktura, invoice_data: dict):
    invoice.ukupna_cijena_osnovna = invoice_data['ukupna_cijena_osnovna']
    invoice.ukupna_cijena_rabatisana = invoice_data['ukupna_cijena_rabatisana']
    invoice.ukupna_cijena_puna = invoice_data['ukupna_cijena_puna']
    invoice.ukupna_cijena_prodajna = invoice_data['ukupna_cijena_prodajna']
    invoice.porez_iznos = invoice_data['porez_iznos']
    invoice.rabat_iznos_osnovni = invoice_data['rabat_iznos_osnovni']
    invoice.rabat_iznos_prodajni = invoice_data['rabat_iznos_prodajni']
    invoice.tax_exemption_amount = invoice_data['tax_exemption_amount']


def formiraj_korigovane_grupe_poreza(faktura: Faktura):
    tax_groups = {}  # Contains tax items
    exemption_groups = {}  # Contains tax exempted items

    for invoice_item in faktura.stavke:
        if invoice_item.tax_exemption_reason_id is None:
            if invoice_item.porez_procenat not in tax_groups:
                tax_group = FakturaGrupaPoreza()
                tax_group.ukupna_cijena_osnovna = 0
                tax_group.ukupna_cijena_rabatisana = 0
                tax_group.ukupna_cijena_puna = 0
                tax_group.ukupna_cijena_prodajna = 0
                tax_group.porez_procenat = invoice_item.porez_procenat
                tax_group.porez_iznos = 0
                tax_group.rabat_iznos_osnovni = 0
                tax_group.rabat_iznos_prodajni = 0
                tax_group.credit_note_turnover_used = 0
                tax_group.credit_note_turnover_remaining = 0
                tax_group.tax_exemption_reason_id = None
                tax_group.tax_exemption_amount = 0
                tax_groups[invoice_item.porez_procenat] = tax_group

            tax_group = tax_groups[invoice_item.porez_procenat]
        else:
            if invoice_item.tax_exemption_reason_id not in exemption_groups:
                tax_group = FakturaGrupaPoreza()
                tax_group.ukupna_cijena_osnovna = 0
                tax_group.ukupna_cijena_rabatisana = 0
                tax_group.ukupna_cijena_puna = 0
                tax_group.ukupna_cijena_prodajna = 0
                tax_group.porez_iznos = 0
                tax_group.rabat_iznos_osnovni = 0
                tax_group.rabat_iznos_prodajni = 0
                tax_group.credit_note_turnover_used = 0
                tax_group.credit_note_turnover_remaining = 0
                tax_group.tax_exemption_reason_id = invoice_item.tax_exemption_reason_id
                tax_group.tax_exemption_amount = 0
                exemption_groups[invoice_item.tax_exemption_reason_id] = tax_group

            tax_group = exemption_groups[invoice_item.tax_exemption_reason_id]

        tax_group.ukupna_cijena_osnovna += invoice_item.korigovana_ukupna_cijena_osnovna
        tax_group.ukupna_cijena_rabatisana += invoice_item.korigovana_ukupna_cijena_rabatisana
        tax_group.ukupna_cijena_puna += invoice_item.korigovana_ukupna_cijena_puna
        tax_group.ukupna_cijena_prodajna += invoice_item.korigovana_ukupna_cijena_prodajna
        tax_group.porez_iznos += invoice_item.korigovani_porez_iznos
        tax_group.rabat_iznos_osnovni += invoice_item.korigovani_rabat_iznos_osnovni
        tax_group.rabat_iznos_prodajni += invoice_item.korigovani_rabat_iznos_prodajni
        tax_group.credit_note_turnover_used += invoice_item.credit_note_turnover_used
        tax_group.credit_note_turnover_remaining += invoice_item.credit_note_turnover_remaining
        tax_group.tax_exemption_amount += invoice_item.corrected_tax_exemption_amount

    return [*tax_groups.values(), *exemption_groups.values()]


def round_half_up(number: Decimal, decimal_places: int):
    quantize_value = Decimal(1) / (Decimal(10) ** Decimal(decimal_places))
    return number.quantize(quantize_value, ROUND_HALF_UP)


def get_rebate_multiplier(rebate_percentage: Decimal):
    return (Decimal(100) - Decimal(rebate_percentage)) / 100


def get_tax_multiplier(tax_percentage: Decimal):
    return tax_percentage / 100 + 1


def update_invoice_item_from_upb(
        item: FakturaStavka,
        quantity: Decimal,
        price: Decimal,
        tax_percentage: Decimal,
        rebate_percentage: Decimal
):
    tax_multiplier = get_tax_multiplier(tax_percentage)
    rebate_multiplier = get_rebate_multiplier(rebate_percentage)
    precision = 4

    item.porez_procenat = tax_percentage
    item.rabat_procenat = rebate_percentage

    item.izvor_kalkulacije = FakturaStavka.IZVOR_KALKULACIJE_UPB
    item.jedinicna_cijena_osnovna = price
    item.jedinicna_cijena_rabatisana = round_half_up(price * rebate_multiplier, precision)
    item.jedinicna_cijena_puna = round_half_up(price * tax_multiplier, precision)
    item.jedinicna_cijena_prodajna = round_half_up(item.jedinicna_cijena_rabatisana * tax_multiplier, precision)

    item.kolicina = quantity
    item.ukupna_cijena_osnovna = round_half_up(item.jedinicna_cijena_osnovna * quantity, precision)
    item.ukupna_cijena_rabatisana = round_half_up(
        item.jedinicna_cijena_osnovna * rebate_multiplier * quantity, precision)
    item.porez_iznos = round_half_up(item.ukupna_cijena_rabatisana * tax_percentage / 100, precision)
    item.ukupna_cijena_prodajna = round_half_up(item.ukupna_cijena_rabatisana + item.porez_iznos, precision)
    item.ukupna_cijena_puna = round_half_up(item.ukupna_cijena_prodajna / rebate_multiplier, precision)
    item.rabat_iznos_osnovni = round_half_up(item.ukupna_cijena_osnovna - item.ukupna_cijena_rabatisana, precision)
    item.rabat_iznos_prodajni = round_half_up(item.ukupna_cijena_puna - item.ukupna_cijena_prodajna, precision)
    item.tax_exemption_amount = Decimal(0.00)

    item.korigovana_kolicina = item.kolicina
    item.korigovana_ukupna_cijena_osnovna = item.ukupna_cijena_osnovna
    item.korigovana_ukupna_cijena_rabatisana = item.ukupna_cijena_rabatisana
    item.korigovana_ukupna_cijena_puna = item.ukupna_cijena_puna
    item.korigovana_ukupna_cijena_prodajna = item.ukupna_cijena_prodajna
    item.korigovani_porez_iznos = item.porez_iznos
    item.korigovani_rabat_iznos_osnovni = item.rabat_iznos_osnovni
    item.korigovani_rabat_iznos_prodajni = item.rabat_iznos_prodajni
    item.corrected_tax_exemption_amount = Decimal(0.00)

    item.credit_note_turnover_used = Decimal(0.00)
    item.credit_note_turnover_remaining = item.ukupna_cijena_prodajna

    return item


def update_invoice_item_from_upa(
        item: FakturaStavka,
        quantity: Decimal,
        price: Decimal,
        tax_percentage: Decimal,
        rebate_percentage: Decimal
):
    tax_multiplier = get_tax_multiplier(tax_percentage)
    rebate_multiplier = get_rebate_multiplier(rebate_percentage)
    precision = 4

    item.porez_procenat = tax_percentage
    item.rabat_procenat = rebate_percentage

    item.izvor_kalkulacije = FakturaStavka.IZVOR_KALKULACIJE_UPA
    item.jedinicna_cijena_puna = price
    item.jedinicna_cijena_prodajna = round_half_up(price * rebate_multiplier, precision)
    item.jedinicna_cijena_rabatisana = round_half_up(item.jedinicna_cijena_prodajna / tax_multiplier, precision)
    item.jedinicna_cijena_osnovna = round_half_up(item.jedinicna_cijena_rabatisana / rebate_multiplier, precision)

    item.kolicina = quantity
    item.ukupna_cijena_prodajna = round_half_up(item.jedinicna_cijena_prodajna * quantity, precision)
    item.ukupna_cijena_rabatisana = round_half_up(item.ukupna_cijena_prodajna / tax_multiplier, precision)
    item.porez_iznos = round_half_up(item.ukupna_cijena_prodajna - item.ukupna_cijena_rabatisana, precision)
    item.ukupna_cijena_puna = round_half_up(item.jedinicna_cijena_puna * quantity, precision)
    item.ukupna_cijena_osnovna = round_half_up(item.ukupna_cijena_rabatisana / rebate_multiplier, precision)
    item.rabat_iznos_prodajni = round_half_up(item.ukupna_cijena_puna - item.ukupna_cijena_prodajna, precision)
    item.rabat_iznos_osnovni = round_half_up(item.ukupna_cijena_osnovna - item.ukupna_cijena_rabatisana, precision)
    item.tax_exemption_amount = Decimal(0.00)

    item.korigovana_kolicina = item.kolicina
    item.korigovana_ukupna_cijena_osnovna = item.ukupna_cijena_osnovna
    item.korigovana_ukupna_cijena_rabatisana = item.ukupna_cijena_rabatisana
    item.korigovana_ukupna_cijena_puna = item.ukupna_cijena_puna
    item.korigovana_ukupna_cijena_prodajna = item.ukupna_cijena_prodajna
    item.korigovani_porez_iznos = item.porez_iznos
    item.korigovani_rabat_iznos_osnovni = item.rabat_iznos_osnovni
    item.korigovani_rabat_iznos_prodajni = item.rabat_iznos_prodajni
    item.corrected_tax_exemption_amount = Decimal(0.00)

    item.credit_note_turnover_used = Decimal(0.00)
    item.credit_note_turnover_remaining = item.ukupna_cijena_prodajna

    return item


def update_invoice_item_from_tax_exemption_amount(
    item: FakturaStavka,
    quantity: Decimal,
    price: Decimal,
    rebate_percentage: Decimal,
    tax_exemption_reason: TaxExemptionReason
):
    item = update_invoice_item_from_upb(item, quantity, price, Decimal(0), rebate_percentage)
    item.tax_exemption_amount = item.ukupna_cijena_prodajna
    item.corrected_tax_exemption_amount = item.ukupna_cijena_prodajna
    item.tax_exemption_reason = tax_exemption_reason

    return item


def get_mailing_campaign_by_id(campaign_id: int) -> t.Union[FakturaMailKampanja, None]:
    return db.session.query(FakturaMailKampanja) \
        .filter(FakturaMailKampanja.id == campaign_id) \
        .first()


def get_mailing_campaign_item_by_id(campaign_id: int) -> t.List[FakturaMailKampanjaStavka]:
    return db.session.query(FakturaMailKampanjaStavka) \
        .filter(FakturaMailKampanjaStavka.faktura_mail_kampanja_id == campaign_id) \
        .all()


def set_mailing_campaign_id_success(campaign_item: FakturaMailKampanjaStavka) -> None:
    campaign_item.status = FakturaMailKampanjaStavka.STATUS_SUCCESS
    db.session.add(campaign_item)
    db.session.commit()


def set_mailing_campaign_id_fail(campaign_item: FakturaMailKampanjaStavka, error_message: str) -> None:
    campaign_item.status = FakturaMailKampanjaStavka.STATUS_FAIL
    campaign_item.opis_greske = error_message
    db.session.add(campaign_item)
    db.session.commit()
