import typing as t
import uuid as uuid_gen
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.parse import urlunsplit

import pymysql
import requests
from OpenSSL.crypto import Error as OpenSSLCryptoError
from sqlalchemy import exc
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import orm

from backend import calc
from backend import efi_xml
from backend import enums
from backend import fiskalizacija
from backend import i18n
from backend import stampa
from backend.db import db
from backend.logging import logger
from backend.models import CreditNoteProcessingLock, CreditNoteIICRef, OrdinalNumberCounter
from backend.models import CreditNoteRequest
from backend.models import CreditNoteResponse
from backend.models import Faktura
from backend.models import Firma
from backend.models import KnjiznoOdobrenje
from backend.models import KnjiznoOdobrenjeGrupaPoreza
from backend.models import KnjiznoOdobrenjeStavka
from backend.models import Komitent
from backend.models import NaplatniUredjaj
from backend.models import Operater
from backend.models import Valuta
from backend.opb import certificate_opb
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja


class CreditNoteProcessingError(Exception):

    def __init__(
            self,
            messages: t.Dict[str, str],
            instance: t.Optional[KnjiznoOdobrenje] = None,
            original_exception: t.Optional[Exception] = None,
            locale: t.Optional[str] = i18n.DEFAULT_LOCALE
    ):
        self.instance = instance
        self.messages = messages
        self.original_exception = original_exception

        super(CreditNoteProcessingError, self).__init__(self.get_message(locale))

    def get_message(self, locale: t.Optional[str] = i18n.DEFAULT_LOCALE):
        return self.messages.get(locale)


class CreditNoteProcessing:

    def __init__(self, locale: t.Optional[str] = i18n.DEFAULT_LOCALE):
        self.locale = locale
        self.is_success = False
        self.messages = None

    @contextmanager
    def acquire_lock(
            self,
            payment_device_id: int,
            session: t.Optional[orm.Session] = None,
            safe: t.Optional[bool] = True
    ):
        session = session or db.create_session()

        try:
            session.query(CreditNoteProcessingLock).with_for_update().get(payment_device_id)
            logger.info('Lock on payment device #%s activated' % payment_device_id)
        except pymysql.err.OperationalError:
            session.commit()
            logger.exception('Error acquiring credit note processing lock on payment device #%s' % payment_device_id)
            raise
        except Exception:
            session.commit()
            logger.exception('Error acquiring credit note processing lock on payment device #%s' % payment_device_id)
            raise

        try:
            yield session
            self.is_success = True
            self.messages = {
                i18n.LOCALE_SR_LATN_ME: 'Knjižno odobrenje je fiskalizovano',
                i18n.LOCALE_EN_US: 'Credit note is fiscalized'
            }
        except CreditNoteProcessingError as exception:
            self.is_success = False
            self.messages = exception.messages

            logger.exception('Credit note processing error on payment device #%s' % payment_device_id)
            if not safe:
                raise
        except Exception:
            self.is_success = False
            self.messages = {
                i18n.LOCALE_SR_LATN_ME: 'Došlo je do nepredviđene greške. Molimo kontaktirajte tehničku podršku.',
                i18n.LOCALE_EN_US: 'Unknown error occurred. Please contact technical support.',
            }

            logger.exception('Unknown credit note processing error on payment device #%s' % payment_device_id)
            if not safe:
                raise
        finally:
            session.commit()
            logger.info('Lock on payment device #%s deactivated' % payment_device_id)

    def get_message(self, locale: t.Optional[str] = i18n.DEFAULT_LOCALE):
        return self.messages[locale]


def get_next_ordinal_number(
        type_id: int,
        payment_device_id: int,
        year: int,
        session: orm.Session
) -> int:
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
        session.add(counter)

    counter.last_value += 1
    session.add(counter)

    return counter.last_value


def get_iic_refs_by_id(credit_note_id: int) -> t.List[CreditNoteIICRef]:
    return db.session.query(CreditNoteIICRef) \
        .filter(CreditNoteIICRef.credit_note_id == credit_note_id) \
        .all()


def _get_xml_request_or_raise(credit_note: KnjiznoOdobrenje):
    db_certificate = certificate_opb.get_certificate_by_customer(credit_note.firma, credit_note.datum_fiskalizacije)
    if db_certificate is None:
        raise CreditNoteProcessingError(
            messages={
                i18n.LOCALE_SR_LATN_ME: 'Nije moguće potpisati knjižno odobrenje jer no postoji ispravan sertifikat za potpisavanje za aktuelni period.',
                i18n.LOCALE_EN_US: 'It is not possible to sign the credit note because there is no valid signing certificate for the current period.',
            }
        )

    try:
        private_key, certificate, _ = fiskalizacija.from_certificate_store(db_certificate.fingerprint, db_certificate.password)
    except OpenSSLCryptoError:
        raise CreditNoteProcessingError(
            messages={
                i18n.LOCALE_SR_LATN_ME: 'Greška prilikom pristupa sertifikatu za potpisivanje.',
                i18n.LOCALE_EN_US: 'Error while trying to access certificate.',
            }
        )

    iic_digest, iic_signature = fiskalizacija.get_iic_digest_and_signature(get_iic_params(credit_note), private_key)
    credit_note.iic = iic_digest
    credit_note.ikof = iic_digest

    db.session.add(credit_note)
    db.session.commit()

    try:
        unsinged_xml = efi_xml.generate_register_credit_note(credit_note, iic_signature)
        unsigned_xml_bytes = efi_xml.tostring(unsinged_xml)
    except Exception as exception:
        raise CreditNoteProcessingError(
            instance=credit_note,
            original_exception=exception,
            messages={
                i18n.LOCALE_SR_LATN_ME:
                    'Došlo je do greške prilikom formiranja poruke za prijavu računa poreskoj upravi.',
                i18n.LOCALE_EN_US:
                    'Error occurred while formatting message.',
            })

    # TODO Do we need to keep unsinged XML request as file?
    if podesavanja.EFI_FILES_STORE is not None:
        filepath = Path(podesavanja.EFI_FILES_STORE, 'credit_note_%s__request_unsigned.xml' % credit_note.id)
        with open(filepath, 'wb') as f:
            f.write(unsigned_xml_bytes)

    try:
        signed_xml = fiskalizacija.potpisi(unsinged_xml, private_key, certificate)
        signed_xml_bytes = efi_xml.tostring(signed_xml)
    except Exception as exception:
        raise CreditNoteProcessingError(
            instance=credit_note,
            original_exception=exception,
            messages={
                i18n.LOCALE_SR_LATN_ME:
                    'Došlo je do greške prilikom potpisivanja poruke za prijavu računa poreskoj upravi.',
                i18n.LOCALE_EN_US:
                    'Error occured while formatting the message.'
            })

    if podesavanja.EFI_FILES_STORE is not None:
        with open(Path(podesavanja.EFI_FILES_STORE, 'credit_note_%s__request.xml' % credit_note.id), 'wb') as f:
            f.write(signed_xml_bytes)

    return signed_xml_bytes


def get_iic_params(credit_note: KnjiznoOdobrenje):
    return "|".join([
        "%s" % credit_note.firma.pib,
        "%s" % credit_note.datum_fiskalizacije,
        "%s" % credit_note.efi_ordinal_number,
        "%s" % credit_note.naplatni_uredjaj.organizaciona_jedinica.efi_kod,
        "%s" % credit_note.naplatni_uredjaj.efi_kod,
        "%s" % podesavanja.EFI_KOD_SOFTVERA,
        "%s" % credit_note.return_and_discount_amount_with_tax
    ]).encode()


def _fiscalize_credit_note(credit_note: KnjiznoOdobrenje, fiscalisation_date: datetime) -> KnjiznoOdobrenje:
    credit_note.uuid = str(uuid_gen.uuid4())
    credit_note.datum_fiskalizacije = fiscalisation_date

    counter_session = db.session()
    if fiscalisation_date.year == 2024:
        credit_note.efi_ordinal_number = get_next_ordinal_number(
            type_id=enums.OrdinalNumberCounterType.EFI_COUNT.value,
            payment_device_id=credit_note.naplatni_uredjaj_id,
            year=fiscalisation_date.year,
            session=counter_session
        )
        credit_note.internal_ordinal_number = get_next_ordinal_number(
            type_id=enums.OrdinalNumberCounterType.CREDIT_NOTES.value,
            payment_device_id=credit_note.naplatni_uredjaj_id,
            year=fiscalisation_date.year,
            session=counter_session
        )
    else:
        ordinal_number = get_next_ordinal_number(
            type_id=enums.OrdinalNumberCounterType.CREDIT_NOTES.value,
            payment_device_id=credit_note.naplatni_uredjaj_id,
            year=fiscalisation_date.year,
            session=counter_session
        )
        credit_note.efi_ordinal_number = ordinal_number
        credit_note.internal_ordinal_number = ordinal_number

    credit_note.efi_broj_fakture = '%s/%s/%s/%s' % (
        credit_note.naplatni_uredjaj.organizaciona_jedinica.efi_kod,
        credit_note.efi_ordinal_number,
        credit_note.datum_fiskalizacije.year,
        credit_note.naplatni_uredjaj.efi_kod
    )

    _xml_request = _get_xml_request_or_raise(credit_note)

    try:
        _send_request_to_tax_office(credit_note, _xml_request)
    except (Exception, CreditNoteProcessingError):
        counter_session.rollback()
        raise

    if credit_note.jikr is None:
        counter_session.rollback()
        response = listaj_efi_odgovor(credit_note.id)
        raise CreditNoteProcessingError(
            instance=credit_note,
            messages={
                i18n.LOCALE_SR_LATN_ME: efi_xml.xml_error_to_string(response.faultcode),
                i18n.LOCALE_EN_US: efi_xml.xml_error_to_string(response.faultcode, lang=i18n.LOCALE_EN_US),
            })

    counter_session.commit()

    return credit_note


def _send_request_to_tax_office(credit_note: KnjiznoOdobrenje, xml_request: bytes) -> KnjiznoOdobrenje:
    request = CreditNoteRequest()
    request.uuid = str(uuid_gen.uuid4())
    request.knjizno_odobrenje = credit_note
    db.session.add(request)
    db.session.commit()

    if podesavanja.EFI_FILES_STORE is not None:
        with open(Path(podesavanja.EFI_FILES_STORE, 'credit_note_%s__request.xml' % credit_note.id), 'wb') as f:
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
        raise CreditNoteProcessingError(
            original_exception=connection_error,
            instance=credit_note,
            messages={
                i18n.LOCALE_SR_LATN_ME: "Došlo je do greške u komunikaciji sa servisom poreske uprave.",
                i18n.LOCALE_EN_US: 'Tax administration office service is unavailable. Please try again later.',
            })
    except Exception as exception:
        raise CreditNoteProcessingError(
            instance=credit_note,
            original_exception=exception,
            messages={
                i18n.LOCALE_SR_LATN_ME: "Došlo je do nepoznate greške.",
                i18n.LOCALE_EN_US: 'Unknown error',
            })

    if podesavanja.EFI_FILES_STORE is not None:
        with open(Path(podesavanja.EFI_FILES_STORE, 'credit_note_%s__response.xml' % credit_note.id), 'wb') as f:
            f.write(response.content)

    response_uuid, faultcode, faultstring, jikr = efi_xml.read_register_invoice_response(response.content.decode())

    register_invoice_response = CreditNoteResponse()
    register_invoice_response.knjizno_odobrenje = credit_note
    register_invoice_response.uuid = response_uuid
    register_invoice_response.register_invoice_request_id = request.id

    if jikr is not None:
        credit_note.jikr = jikr
        credit_note.status = 2

        efi_verify_url_qp = urlencode({
            'iic': credit_note.iic,
            'tin': credit_note.firma.pib,
            'crtd': efi_xml.get_efi_datetime_format(credit_note.datum_fiskalizacije),
            'ord': credit_note.efi_ordinal_number,
            'bu': credit_note.naplatni_uredjaj.organizaciona_jedinica.efi_kod,
            'cr': credit_note.naplatni_uredjaj.efi_kod,
            'sw': podesavanja.EFI_KOD_SOFTVERA,
            'prc': calc.format_decimal(-1*credit_note.return_and_discount_amount_with_tax, 2, 2),
        })

        credit_note.efi_verify_url = urlunsplit((
            podesavanja.EFI_VERIFY_PROTOCOL,
            podesavanja.EFI_VERIFY_URL,
            '',
            efi_verify_url_qp,
            ''
        ))

        db.session.commit()
    else:
        credit_note.status = 3
        register_invoice_response.faultcode = faultcode
        register_invoice_response.faultstring = faultstring
        db.session.commit()

    request.register_invoice_response = register_invoice_response
    db.session.add(register_invoice_response)
    db.session.commit()

    return credit_note


def _validate_create_credit_note(
        firma: Firma,
        podaci: dict
):
    komitent_id = podaci.get('komitent_id')
    komitent = db.session.query(Komitent) \
        .filter(Komitent.pibvlasnikapodatka == firma.pib) \
        .filter(Komitent.id == komitent_id) \
        .first()
    if komitent is None:
        raise Exception('Buyer does not exist.')


def _get_buyer_or_raise(
        pib: str,
        buyer_id: int
) -> Komitent:
    try:
        return db.session.query(Komitent) \
            .filter(Komitent.pibvlasnikapodatka == pib) \
            .filter(Komitent.id == buyer_id) \
            .one()
    except exc.NoResultFound:
        raise CreditNoteProcessingError(messages={
            i18n.LOCALE_SR_LATN_ME: 'Nije pronađen kupac. Mora biti tačno jedan.',
            i18n.LOCALE_EN_US: 'No buyer found. Must be exactly one.'
        })
    except Exception:
        raise CreditNoteProcessingError(messages={
            i18n.LOCALE_SR_LATN_ME: 'Unknown error while searching for buyer.',
            i18n.LOCALE_EN_US: 'Nepoznata greška prilikom pretrage kupca.'
        })


def _get_invoice_for_credit_note_or_raise(
        credit_note: KnjiznoOdobrenje,
        invoice_id: int
) -> Faktura:
    invoice = db.session.query(Faktura).get(invoice_id)
    if invoice is None:
        raise CreditNoteProcessingError(messages={
            i18n.LOCALE_SR_LATN_ME: 'Nije pronađen račun.',
            i18n.LOCALE_EN_US: 'Invoice not found.'
        })

    if invoice.firma_id != credit_note.firma.id:
        raise CreditNoteProcessingError(messages={
            i18n.LOCALE_SR_LATN_ME: 'Nije pronađen račun.',
            i18n.LOCALE_EN_US: 'Invoice not found.'
        })

    if invoice.komitent_id != credit_note.komitent.id:
        raise CreditNoteProcessingError(messages={
            i18n.LOCALE_SR_LATN_ME: 'Nije pronađen račun.',
            i18n.LOCALE_EN_US: 'Invoice not found.'
        })

    if invoice.status == Faktura.STATUS_CANCELLED:
        raise CreditNoteProcessingError({
            i18n.LOCALE_SR_LATN_ME: f'Knjižno odobrenje se ne može fiskalizovati. Referentna invoice '
                                    f'#{invoice.efi_ordinal_number} je stornirana.',
            i18n.LOCALE_EN_US: f'Cannot fiscalize credit note. Referent invoice #{invoice.efi_ordinal_number} '
                               f'is canceled.'
        })

    if invoice.status != Faktura.STATUS_FISCALISATION_SUCCESS:
        raise CreditNoteProcessingError({
            i18n.LOCALE_SR_LATN_ME: f'Knjižno odobrenje se ne može fiskalizovati. Faktura '
                                    f'#{invoice.efi_ordinal_number} nije u ispravnom statusu '
                                    f'(status={invoice.status}).',
            i18n.LOCALE_EN_US: f'Cannot fiscalize credit note. Invoice #{invoice.efi_ordinal_number} has invalid '
                               f'status. ({invoice.status})'
        })

    return invoice


def _get_currency_or_raise(currency_id: int) -> Valuta:
    currency = db.session.query(Valuta).get(currency_id)
    if currency is None:
        raise CreditNoteProcessingError({
            i18n.LOCALE_SR_LATN_ME: 'Valuta nije pronađena.',
            i18n.LOCALE_EN_US: 'Currency not found.'
        })
    return currency


def _create_credit_note(
        firma: Firma,
        operater: Operater,
        naplatni_uredjaj: NaplatniUredjaj,
        podaci: dict
) -> KnjiznoOdobrenje:
    knjizno_odobrenje = KnjiznoOdobrenje()
    knjizno_odobrenje.status = 1
    knjizno_odobrenje.naplatni_uredjaj = naplatni_uredjaj
    knjizno_odobrenje.firma = firma
    knjizno_odobrenje.operater = operater
    knjizno_odobrenje.efi_ordinal_number = None
    knjizno_odobrenje.efi_internal_number = None
    knjizno_odobrenje.datum_fiskalizacije = None

    current_time = datetime.now()
    knjizno_odobrenje.datum_prometa = current_time
    knjizno_odobrenje.datum_valute = current_time
    knjizno_odobrenje.poreski_period = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

    knjizno_odobrenje.valuta = _get_currency_or_raise(podaci['valuta_id'])
    if knjizno_odobrenje.valuta.id == Valuta.DOMESTIC_CURRENCY_ID:
        knjizno_odobrenje.kurs_razmjene = 1
    else:
        knjizno_odobrenje.kurs_razmjene = podaci['kurs_razmjene']

    knjizno_odobrenje.komitent = _get_buyer_or_raise(firma.pib, podaci['komitent_id'])
    knjizno_odobrenje.tax_amount = podaci['tax_amount']
    knjizno_odobrenje.return_amount = podaci['return_amount']
    knjizno_odobrenje.return_amount_with_tax = podaci['return_amount_with_tax']
    knjizno_odobrenje.discount_amount = podaci['discount_amount']
    knjizno_odobrenje.discount_amount_with_tax = podaci['discount_amount_with_tax']
    knjizno_odobrenje.return_and_discount_amount = podaci['return_and_discount_amount']
    knjizno_odobrenje.return_and_discount_amount_with_tax = podaci['return_and_discount_amount_with_tax']

    # for invoice_id in podaci['invoice_ids']:
    #     knjizno_odobrenje.fakture.append(
    #         _get_invoice_for_credit_note_or_raise(knjizno_odobrenje, invoice_id))

    item_counter = {}

    for podaci_stavka in podaci.get('stavke'):
        knjizno_odobrenje_stavka = KnjiznoOdobrenjeStavka()
        knjizno_odobrenje_stavka.description = podaci_stavka['description']
        knjizno_odobrenje_stavka.type = podaci_stavka['type']
        knjizno_odobrenje_stavka.tax_rate = podaci_stavka['tax_rate']
        knjizno_odobrenje_stavka.tax_amount = podaci_stavka['tax_amount']
        knjizno_odobrenje_stavka.return_amount = podaci_stavka['return_amount']
        knjizno_odobrenje_stavka.return_amount_with_tax = podaci_stavka['return_amount_with_tax']
        knjizno_odobrenje_stavka.discount_amount = podaci_stavka['discount_amount']
        knjizno_odobrenje_stavka.discount_amount_with_tax = podaci_stavka['discount_amount_with_tax']
        knjizno_odobrenje.stavke.append(knjizno_odobrenje_stavka)

        if knjizno_odobrenje_stavka.tax_rate not in item_counter:
            item_counter[knjizno_odobrenje_stavka.tax_rate] = 0
        item_counter[knjizno_odobrenje_stavka.tax_rate] += 1

    for iic_ref_dict in podaci['iic_refs']:
        iic_ref = CreditNoteIICRef()
        iic_ref.iic = iic_ref_dict['iic']
        iic_ref.invoice_id = iic_ref_dict['invoice_id']
        iic_ref.verification_url = iic_ref_dict['verification_url']
        iic_ref.issue_datetime = datetime.fromisoformat(iic_ref_dict['issue_datetime'])
        iic_ref.amount_21 = iic_ref_dict['amount_21']
        iic_ref.amount_7 = iic_ref_dict['amount_7']
        iic_ref.amount_0 = iic_ref_dict['amount_0']
        iic_ref.amount_exempt = iic_ref_dict['amount_exempt']
        iic_ref.total_21 = iic_ref_dict['total_21']
        iic_ref.total_7 = iic_ref_dict['total_7']
        iic_ref.total_0 = iic_ref_dict['total_0']
        iic_ref.total_exempt = iic_ref_dict['total_exempt']
        iic_ref.credit_note = knjizno_odobrenje
        db.session.add(iic_ref)
        db.session.commit()

    for stavka in podaci['grupe_poreza']:
        tax_group = KnjiznoOdobrenjeGrupaPoreza()
        tax_group.broj_stavki = item_counter[stavka['tax_rate']]

        tax_group.tax_rate = stavka['tax_rate']
        tax_group.tax_amount = stavka['tax_amount']
        tax_group.return_amount = stavka['return_amount']
        tax_group.return_amount_with_tax = stavka['return_amount_with_tax']
        tax_group.discount_amount = stavka['discount_amount']
        tax_group.discount_amount_with_tax = stavka['discount_amount_with_tax']
        tax_group.return_and_discount_amount = stavka['return_and_discount_amount']
        tax_group.return_and_discount_amount_with_tax = stavka['return_and_discount_amount_with_tax']
        knjizno_odobrenje.grupe_poreza.append(tax_group)

    return knjizno_odobrenje


def _update_invoice_turnover(credit_note: KnjiznoOdobrenje):
    for ref in credit_note.iic_refs:
        if ref.invoice_id is not None:
            ref.invoice.credit_note_turnover_remaining = (
                    ref.invoice.credit_note_turnover_remaining
                    - ref.amount_21
                    - ref.amount_7
                    - ref.amount_0
                    - ref.amount_exempt)

            db.session.add(ref.invoice)
            for tax_group in ref.invoice.grupe_poreza:
                if tax_group.porez_procenat == 21:
                    tax_group.credit_note_turnover_remaining -= ref.amount_21
                elif tax_group.porez_procenat == 7:
                    tax_group.credit_note_turnover_remaining -= ref.amount_7
                elif tax_group.porez_procenat == 0:
                    tax_group.credit_note_turnover_remaining -= ref.amount_0
                elif tax_group.porez_procenat is None:
                    tax_group.credit_note_turnover_remaining -= ref.amount_exempt
                db.session.add(tax_group)
    db.session.commit()
    # cn_turnover = credit_note.return_and_discount_amount_with_tax
    # for faktura in credit_note.fakture:
    #     faktura.status = Faktura.STATUS_IN_CREDIT_NOTE
    #     if cn_turnover < faktura.credit_note_turnover_remaining:
    #         faktura.credit_note_turnover_remaining = faktura.credit_note_turnover_remaining - cn_turnover
    #         faktura.credit_note_turnover_used = cn_turnover
    #         cn_turnover = 0
    #     else:
    #         faktura.credit_note_turnover_used = faktura.credit_note_turnover_remaining
    #         cn_turnover = cn_turnover - faktura.credit_note_turnover_remaining
    #         faktura.credit_note_turnover_remaining = 0
    #
    # for credit_note_tax_group in credit_note.grupe_poreza:
    #     cn_tax_group_turnover = credit_note_tax_group.return_and_discount_amount_with_tax
    #     for faktura in credit_note.fakture:
    #         for faktura_stavka in faktura.stavke:
    #             if faktura_stavka.porez_procenat != credit_note_tax_group.tax_rate:
    #                 continue
    #
    #             if cn_tax_group_turnover < faktura_stavka.credit_note_turnover_remaining:
    #                 faktura_stavka.credit_note_turnover_remaining = faktura_stavka.credit_note_turnover_remaining - cn_tax_group_turnover
    #                 faktura_stavka.credit_note_turnover_used = cn_tax_group_turnover
    #                 cn_tax_group_turnover = 0
    #             else:
    #                 faktura_stavka.credit_note_turnover_used = faktura_stavka.credit_note_turnover_remaining
    #                 cn_tax_group_turnover = cn_tax_group_turnover - faktura_stavka.credit_note_turnover_remaining
    #                 faktura_stavka.credit_note_turnover_remaining = 0
    #
    # for credit_note_tax_group in credit_note.grupe_poreza:
    #     cn_tax_group_turnover = credit_note_tax_group.return_and_discount_amount_with_tax
    #     for faktura in credit_note.fakture:
    #         for faktura_grupa_poreza in faktura.grupe_poreza:
    #             if faktura_grupa_poreza.porez_procenat != credit_note_tax_group.tax_rate:
    #                 continue
    #
    #             if cn_tax_group_turnover < faktura_grupa_poreza.credit_note_turnover_remaining:
    #                 faktura_grupa_poreza.credit_note_turnover_remaining = faktura_grupa_poreza.credit_note_turnover_remaining - cn_tax_group_turnover
    #                 faktura_grupa_poreza.credit_note_turnover_used = cn_tax_group_turnover
    #                 cn_tax_group_turnover = 0
    #             else:
    #                 faktura_grupa_poreza.credit_note_turnover_used = faktura_grupa_poreza.credit_note_turnover_remaining
    #                 cn_tax_group_turnover = cn_tax_group_turnover - faktura_grupa_poreza.credit_note_turnover_remaining
    #                 faktura_grupa_poreza.credit_note_turnover_remaining = 0
    # db.session.commit()


def get_credit_note_by_id(credit_note_id: int) -> KnjiznoOdobrenje:
    return db.session.query(KnjiznoOdobrenje) \
        .filter(KnjiznoOdobrenje.id == credit_note_id) \
        .first()


def get_credit_notes_by_payment_device_id(payment_device_id):
    return db.session.query(KnjiznoOdobrenje) \
        .filter(KnjiznoOdobrenje.naplatni_uredjaj_id == payment_device_id) \
        .filter(KnjiznoOdobrenje.status == KnjiznoOdobrenje.STATUS_FISKALIZOVANO) \
        .all()


def get_customer_view_items(
        payment_device_id: int,
        page_number: int,
        items_per_page: int
):
    q1 = db.session.query(
        Faktura.id.label('id'),
        func.year(Faktura.datumfakture).label('year'),
        Faktura.efi_ordinal_number.label('ordinal_number'),
        literal('invoice').label('type')
    ) \
        .filter(Faktura.naplatni_uredjaj_id == payment_device_id) \
        .filter(Faktura.customer_invoice_view == enums.CustomerInvoiceView.CREDIT_NOTES.value) \
        .filter(Faktura.status.in_([Faktura.STATUS_FISCALISATION_SUCCESS]))

    q2 = db.session.query(
        KnjiznoOdobrenje.id.label('id'),
        func.year(KnjiznoOdobrenje.datum_fiskalizacije).label('year'),
        KnjiznoOdobrenje.efi_ordinal_number.label('ordinal_number'),
        literal('credit_note').label('type')
    ) \
        .filter(KnjiznoOdobrenje.naplatni_uredjaj_id == payment_device_id) \
        .filter(KnjiznoOdobrenje.status == KnjiznoOdobrenje.STATUS_FISKALIZOVANO)

    items_query = q1.union(q2)

    total_items = items_query.count()

    items = items_query \
        .order_by('year', 'ordinal_number') \
        .limit(items_per_page) \
        .offset((page_number - 1) * items_per_page) \
        .all()

    invoice_ids = [item.id for item in items if item.type == 'invoice']
    q1 = db.session.query(Faktura) \
        .filter(Faktura.id.in_(invoice_ids)) \
        .all()

    credit_note_ids = [item.id for item in items if item.type == 'credit_note']
    q2 = db.session.query(KnjiznoOdobrenje) \
        .filter(KnjiznoOdobrenje.id.in_(credit_note_ids)) \
        .all()

    def custom_sort_key(item):
        if isinstance(item, Faktura):
            return -item.datumfakture.year, -item.efi_ordinal_number
        if isinstance(item, KnjiznoOdobrenje):
            return -item.datum_fiskalizacije.year, -item.efi_ordinal_number

    return {
        'broj_stranice': page_number,
        'broj_stavki_po_stranici': items_per_page,
        'ukupan_broj_stavki': total_items,
        'stavke': sorted(q1 + q2, key=custom_sort_key)
    }


def listaj_efi_odgovor(credit_note_id: int):
    return db.session.query(CreditNoteResponse) \
        .filter(CreditNoteResponse.knjizno_odobrenje_id == credit_note_id) \
        .first()


def make_credit_note(
        firma: Firma,
        operater: Operater,
        naplatni_uredjaj: NaplatniUredjaj,
        podaci: dict,
        fiscalization_date: datetime = None
):
    credit_note_processing = CreditNoteProcessing()

    credit_note = None
    invoice_processing = faktura_opb.InvoiceProcessing()

    with invoice_processing.acquire_lock(naplatni_uredjaj.id) as _:
        with credit_note_processing.acquire_lock(naplatni_uredjaj.id) as _:
            credit_note = _create_credit_note(firma, operater, naplatni_uredjaj, podaci)
            db.session.add(credit_note)
            db.session.commit()
            logger.info('Created credit note %s' % credit_note.id)

            credit_note = _fiscalize_credit_note(credit_note, fiscalization_date)

            _update_invoice_turnover(credit_note)


            if podesavanja.EFI_FILES_STORE is not None:
                path = Path(podesavanja.EFI_FILES_STORE, 'credit_note_%s__A4.pdf' % credit_note.id)
                stampa.save_credit_note_to_file(credit_note, path)

    return credit_note_processing, credit_note


def get_tax_period_from_dict(data: dict):
    r = datetime.fromisoformat(data['poreski_period'].replace('Z', podesavanja.TIMEZONE))
    return r.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
