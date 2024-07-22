import decimal
import typing as t
from datetime import datetime

from sqlalchemy import func
from sqlalchemy import orm
from sqlalchemy import sql

from backend.db import db
from backend.logging import logger
from backend.models import Artikal, Komitent
from backend.models import Depozit
from backend.models import Faktura
from backend.models import FakturaStavka
from backend.models import GrupaArtikala
from backend.models import KnjiznoOdobrenje
from backend.models import KnjiznoOdobrenjeStavka
from backend.models import MagacinZaliha
from backend.models import PaymentMethod

REPORT_TYPE_CURRENT_STATE = 0
REPORT_TYPE_DAILY_REPORT = 1
REPORT_TYPE_PERIODIC_REPORT = 2

REPORT_TITLE_BY_TYPE = {
    REPORT_TYPE_CURRENT_STATE: 'Presjek stanja',
    REPORT_TYPE_DAILY_REPORT: 'Dnevni izvještaj',
    REPORT_TYPE_PERIODIC_REPORT: 'Periodični izvještaj'
}


def get_intervals(start_datetime, end_datetime):

    if start_datetime.year == end_datetime.year:
        yield start_datetime, end_datetime
        return

    if end_datetime.year - start_datetime.year == 1:
        yield start_datetime, datetime(year=start_datetime.year + 1, month=1, day=1)
        yield datetime(year=end_datetime.year, month=1, day=1), end_datetime
        return

    if end_datetime.year - start_datetime.year > 1:
        yield start_datetime, datetime(year=start_datetime.year + 1, month=1, day=1)
        for year in range(start_datetime.year + 1, end_datetime.year + 1):
            yield datetime(year=year, month=1, day=1), datetime(year=year+1, month=1, day=1)
        yield datetime(year=end_datetime.year, month=1, day=1), end_datetime
        return


def get_invoice(
        start: datetime,
        end: datetime,
        payment_device_id: int,
        tip_fakture_id: int,
        order_by
) -> t.Optional[Faktura]:
    type_clause = sql.or_(
        Faktura.tip_fakture_id == tip_fakture_id,
        Faktura.korigovana_faktura.has(Faktura.tip_fakture_id == tip_fakture_id)
    )

    return db.session.query(Faktura) \
        .filter(Faktura.status.in_([Faktura.STATUS_FISCALISATION_SUCCESS, Faktura.STATUS_CANCELLED])) \
        .filter(Faktura.datumfakture >= start) \
        .filter(Faktura.datumfakture < end) \
        .filter(Faktura.naplatni_uredjaj_id == payment_device_id) \
        .filter(type_clause) \
        .order_by(order_by) \
        .first()


def get_deposit(start: datetime, end: datetime, payment_device_id: int, order_by) -> t.Optional[Depozit]:
    return db.session.query(Depozit) \
        .filter(Depozit.tip_depozita == 1) \
        .filter(Depozit.status == 2) \
        .filter(Depozit.datum_slanja >= start) \
        .filter(Depozit.datum_slanja < end) \
        .filter(Depozit.naplatni_uredjaj_id == payment_device_id) \
        .order_by(order_by) \
        .first()


def get_interval_fiscal_number(start, end, payment_device_id):
    first_invoice = get_invoice(start, end, payment_device_id, Faktura.TYPE_REGULAR, Faktura.datumfakture)
    if first_invoice is None:
        # Nema smisla tražiti zadnju fakturu
        return None, None

    last_invoice = get_invoice(start, end, payment_device_id, Faktura.TYPE_REGULAR, Faktura.datumfakture.desc())

    return first_invoice.efi_ordinal_number, last_invoice.efi_ordinal_number


def get_interval_fiscal_day(start, end, payment_device_id):
    year_start = datetime(year=start.year, month=1, day=1)

    first_invoice_in_year = get_invoice(year_start, end, payment_device_id, Faktura.TYPE_REGULAR, Faktura.datumfakture)
    first_deposit_in_year = get_deposit(year_start, end, payment_device_id, Depozit.datum_slanja)
    if first_invoice_in_year is None and first_deposit_in_year is None:
        return None, None
    elif first_invoice_in_year is None:
        first_fiscal_date = first_deposit_in_year.datum_slanja
    elif first_deposit_in_year is None:
        first_fiscal_date = first_invoice_in_year.datumfakture
    else:
        first_fiscal_date = min(first_invoice_in_year.datumfakture, first_deposit_in_year.datum_slanja)

    first_fiscal_date = first_fiscal_date.replace(hour=0, minute=0, second=0, microsecond=0)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end.replace(hour=0, minute=0, second=0, microsecond=0)

    return \
        1 if start < first_fiscal_date else (start - first_fiscal_date).days + 1, \
        (end - first_fiscal_date).days + 1


def izvjestaj__stanje(naplatni_uredjaj, operater, firma, datum_od: datetime, datum_do: datetime, report_type):
    now = datetime.now()

    fiscal_data = []
    for interval_start, interval_end in get_intervals(datum_od, datum_do):
        fiscal_number_first, fiscal_number_last = \
            get_interval_fiscal_number(interval_start, interval_end, naplatni_uredjaj.id)
        fiscal_day_first, fiscal_day_last = \
            get_interval_fiscal_day(interval_start, interval_end, naplatni_uredjaj.id)

        fiscal_data.append({
            'year': interval_start.year,
            'has_fiscal_days': fiscal_day_first is not None,
            'fiscal_day_first': fiscal_day_first,
            'fiscal_day_last': fiscal_day_last,
            'has_fiscal_numbers': fiscal_number_first is not None,
            'fiscal_number_first': fiscal_number_first,
            'fiscal_number_last': fiscal_number_last
        })

    # -------------------------------------------------------------------------------------------------------------------

    inicijalni_depozit = decimal.Decimal(0)
    podignuta_gotovina = decimal.Decimal(0)

    gotovinski_promet_novcanice = decimal.Decimal(0)
    gotovinski_promet_kreditna_kartica = decimal.Decimal(0)
    gotovinski_promet_order = decimal.Decimal(0)
    gotovina_cijena_prodajna_ostalo = decimal.Decimal(0)
    gotovinski_promet_cijena = decimal.Decimal(0)

    bezgotovinski_cijena_puna = decimal.Decimal(0)
    bezgotovinski_cijena_prodajna = decimal.Decimal(0)
    bezgotovinski_vrsta_virman = decimal.Decimal(0)
    bezgotovinski_vrsta_biznis_kred_kartica = decimal.Decimal(0)
    bezgotovinski_vrsta_jednokratni_vaucer = decimal.Decimal(0)
    bezgotovinski_vrsta_kartica_prodavca = decimal.Decimal(0)
    bezgotovinski_vrsta_order = decimal.Decimal(0)
    bezgotovinski_vrsta_avans = decimal.Decimal(0)
    bezgotovinski_vrsta_faktoring = decimal.Decimal(0)
    bezgotovinski_promet_ostalo = decimal.Decimal(0)

    poreska_stopa_0_promet = decimal.Decimal(0)
    poreska_stopa_0_osnovica = decimal.Decimal(0)
    poreska_stopa_0_iznos_poreza = decimal.Decimal(0)

    poreska_stopa_7_promet = decimal.Decimal(0)
    poreska_stopa_7_osnovica = decimal.Decimal(0)
    poreska_stopa_7_iznos_poreza = decimal.Decimal(0)

    poreska_stopa_21_promet = decimal.Decimal(0)
    poreska_stopa_21_osnovica = decimal.Decimal(0)
    poreska_stopa_21_iznos_poreza = decimal.Decimal(0)

    oslobodjeni_promet = decimal.Decimal(0)

    ukupno_prodajna_cijena = decimal.Decimal(0)
    ukupno_puna_cijena = decimal.Decimal(0)

    korektivni_racun_broj = decimal.Decimal(0)
    korektivni_racun_promet = decimal.Decimal(0)
    korektivni_racun_porez = decimal.Decimal(0)

    deposits = db.session.query(Depozit) \
        .filter(Depozit.naplatni_uredjaj_id == naplatni_uredjaj.id) \
        .filter(Depozit.datum_slanja >= datum_od) \
        .filter(Depozit.datum_slanja <= datum_do) \
        .filter(Depozit.status == Depozit.STATUS_FISCALISE_SUCCESS) \
        .all()

    for deposit in deposits:
        if deposit.tip_depozita == 1:
            inicijalni_depozit += deposit.iznos
        elif deposit.tip_depozita == 2:
            podignuta_gotovina += deposit.iznos

    invoice_types = [
        Faktura.TYPE_REGULAR,
        Faktura.TYPE_ADVANCE,
        Faktura.TYPE_CANCELLATION,
        Faktura.TYPE_CORRECTIVE
    ]

    corrective_invoice_types = [
        Faktura.TYPE_CANCELLATION,
        Faktura.TYPE_CORRECTIVE
    ]

    invoices: t.Iterable[Faktura] = db.session.query(Faktura) \
        .options(orm.subqueryload(Faktura.payment_methods), orm.subqueryload(Faktura.stavke)) \
        .filter(Faktura.datumfakture >= datum_od) \
        .filter(Faktura.datumfakture <= datum_do) \
        .filter(Faktura.naplatni_uredjaj_id == naplatni_uredjaj.id) \
        .filter(Faktura.status.in_([
            Faktura.STATUS_FISCALISATION_SUCCESS,
            Faktura.STATUS_CANCELLED,
            Faktura.STATUS_HAS_ERROR_CORRECTIVE,
            Faktura.STATUS_IN_CREDIT_NOTE
        ])) \
        .all()

    for invoice in invoices:
        if invoice.status == Faktura.STATUS_HAS_ERROR_CORRECTIVE:
            invoice.error_corrective_invoice.tip_fakture_id = invoice.tip_fakture_id
            # invoice.error_corrective_invoice.korektivne_fakture = invoice.korektivne_fakture
            # invoice.error_corrective_invoice.korigovana_faktura = invoice.korigovana_faktura
            invoice = invoice.error_corrective_invoice

        if invoice.tip_fakture_id in invoice_types:
            if invoice.is_cash:
                gotovinski_promet_cijena += invoice.ukupna_cijena_puna

                for payment_method in invoice.payment_methods:
                    if payment_method.payment_method_type_id == PaymentMethod.TYPE_BANKNOTE:
                        gotovinski_promet_novcanice += payment_method.amount
                    elif payment_method.payment_method_type_id == PaymentMethod.TYPE_CARD:
                        gotovinski_promet_kreditna_kartica += payment_method.amount
                    elif payment_method.payment_method_type_id == PaymentMethod.TYPE_ORDER:
                        gotovinski_promet_order += payment_method.amount
                    else:
                        gotovina_cijena_prodajna_ostalo += payment_method.amount
            else:
                bezgotovinski_cijena_puna += invoice.ukupna_cijena_puna
                bezgotovinski_cijena_prodajna += invoice.ukupna_cijena_prodajna

                for payment_method in invoice.payment_methods:
                    if payment_method.payment_method_type_id == PaymentMethod.TYPE_BUSINESSCARD:
                        bezgotovinski_vrsta_biznis_kred_kartica += payment_method.amount
                    elif payment_method.payment_method_type_id == PaymentMethod.TYPE_SVOUCHER:
                        bezgotovinski_vrsta_jednokratni_vaucer += payment_method.amount
                    elif payment_method.payment_method_type_id == PaymentMethod.TYPE_COMPANY:
                        bezgotovinski_vrsta_kartica_prodavca += payment_method.amount
                    elif payment_method.payment_method_type_id == PaymentMethod.TYPE_ORDER:
                        bezgotovinski_vrsta_order += payment_method.amount
                    elif payment_method.payment_method_type_id == PaymentMethod.TYPE_ADVANCE:
                        bezgotovinski_vrsta_avans += payment_method.amount
                    elif payment_method.payment_method_type_id == PaymentMethod.TYPE_ACCOUNT:
                        bezgotovinski_vrsta_virman += payment_method.amount
                    elif payment_method.payment_method_type_id == PaymentMethod.TYPE_FACTORING:
                        bezgotovinski_vrsta_faktoring += payment_method.amount
                    else:
                        bezgotovinski_promet_ostalo += payment_method.amount

            ukupno_puna_cijena += invoice.ukupna_cijena_puna
            ukupno_prodajna_cijena += invoice.ukupna_cijena_prodajna

            for invoice_item in invoice.stavke:
                if invoice_item.tax_exemption_reason_id is not None:
                    oslobodjeni_promet += invoice_item.ukupna_cijena_prodajna
                elif invoice_item.porez_procenat == 0:
                    poreska_stopa_0_osnovica += invoice_item.ukupna_cijena_rabatisana
                    poreska_stopa_0_iznos_poreza += invoice_item.porez_iznos
                    poreska_stopa_0_promet += invoice_item.ukupna_cijena_prodajna
                elif invoice_item.porez_procenat == 7:
                    poreska_stopa_7_osnovica += invoice_item.ukupna_cijena_rabatisana
                    poreska_stopa_7_iznos_poreza += invoice_item.porez_iznos
                    poreska_stopa_7_promet += invoice_item.ukupna_cijena_prodajna
                elif invoice_item.porez_procenat == 21:
                    poreska_stopa_21_osnovica += invoice_item.ukupna_cijena_rabatisana
                    poreska_stopa_21_iznos_poreza += invoice_item.porez_iznos
                    poreska_stopa_21_promet += invoice_item.ukupna_cijena_prodajna

        if invoice.tip_fakture_id in corrective_invoice_types:
            korektivni_racun_broj += 1
            korektivni_racun_promet += invoice.ukupna_cijena_prodajna
            korektivni_racun_porez += invoice.porez_iznos

    credit_notes: t.Iterable[KnjiznoOdobrenje] = db.session.query(KnjiznoOdobrenje) \
        .options(orm.subqueryload(KnjiznoOdobrenje.stavke)) \
        .filter(KnjiznoOdobrenje.datum_fiskalizacije >= datum_od) \
        .filter(KnjiznoOdobrenje.datum_fiskalizacije <= datum_do) \
        .filter(KnjiznoOdobrenje.naplatni_uredjaj_id == naplatni_uredjaj.id) \
        .filter(KnjiznoOdobrenje.status.in_([
            KnjiznoOdobrenje.STATUS_FISKALIZOVANO,
        ])) \
        .all()
    for credit_note in credit_notes:
        ukupno_puna_cijena += -1 * credit_note.return_and_discount_amount_with_tax
        ukupno_prodajna_cijena += -1 * credit_note.return_and_discount_amount_with_tax
        bezgotovinski_cijena_puna += -1 * credit_note.return_and_discount_amount_with_tax
        bezgotovinski_cijena_prodajna += -1 * credit_note.return_and_discount_amount
        bezgotovinski_vrsta_virman += -1 * credit_note.return_and_discount_amount_with_tax

        for credit_note_item in credit_note.stavke:
            amount = 0
            amount_with_tax = 0
            if credit_note_item.type == KnjiznoOdobrenjeStavka.ITEM_TYPE_RETURN:
                amount = credit_note_item.return_amount
                amount_with_tax = credit_note_item.return_amount_with_tax
            elif credit_note_item.type == KnjiznoOdobrenjeStavka.ITEM_TYPE_DISCOUNT:
                amount = credit_note_item.discount_amount
                amount_with_tax = credit_note_item.discount_amount_with_tax

            if credit_note_item.tax_rate == 0:
                poreska_stopa_0_osnovica += -1 * amount
                poreska_stopa_0_iznos_poreza += -1 * credit_note_item.tax_amount
                poreska_stopa_0_promet += -1 * amount_with_tax
            elif credit_note_item.tax_rate == 7:
                poreska_stopa_7_osnovica += -1 * amount
                poreska_stopa_7_iznos_poreza += -1 * credit_note_item.tax_amount
                poreska_stopa_7_promet += -1 * amount_with_tax
            elif credit_note_item.tax_rate == 21:
                poreska_stopa_21_osnovica += -1 * amount
                poreska_stopa_21_iznos_poreza += -1 * credit_note_item.tax_amount
                poreska_stopa_21_promet += -1 * amount_with_tax

    # TODO: Da li ovo treba raditi? Korekcija može biti i uvećanje iznosa.
    korektivni_racun_promet = abs(korektivni_racun_promet)
    korektivni_racun_porez = abs(korektivni_racun_porez)

    gotovina_u_enu = inicijalni_depozit + gotovinski_promet_novcanice - podignuta_gotovina
    gotovinski_promet_bez_novcanica = \
        gotovinski_promet_kreditna_kartica \
        + gotovinski_promet_order \
        + gotovina_cijena_prodajna_ostalo
    gotovinski_promet_za_uplatu = \
        gotovinski_promet_novcanice + \
        gotovinski_promet_kreditna_kartica + \
        gotovina_cijena_prodajna_ostalo
    gotovinski_promet_popust = gotovinski_promet_cijena - gotovinski_promet_za_uplatu

    bezgotovinski_popust = bezgotovinski_cijena_puna - bezgotovinski_cijena_prodajna

    ukupno_popust = ukupno_puna_cijena - ukupno_prodajna_cijena
    ukupan_porez_osnovica = \
        poreska_stopa_7_osnovica + \
        poreska_stopa_0_osnovica + \
        poreska_stopa_21_osnovica
    ukupan_porez_iznos = \
        poreska_stopa_7_iznos_poreza + \
        poreska_stopa_0_iznos_poreza + \
        poreska_stopa_21_iznos_poreza
    ukupan_porez_promet = \
        poreska_stopa_0_promet + \
        poreska_stopa_7_promet + \
        poreska_stopa_21_promet

    # TODO Oslobđeni promet

    result = {
        'fiscal_data': fiscal_data,

        'datum_od': datum_od,
        'datum_do': datum_do,
        'poreski_obaveznik': naplatni_uredjaj.organizaciona_jedinica.firma.naziv,
        'sjediste_obaveznika': '%s, %s' % (naplatni_uredjaj.organizaciona_jedinica.firma.adresa, naplatni_uredjaj.organizaciona_jedinica.firma.grad),
        'pib': naplatni_uredjaj.organizaciona_jedinica.firma.pib,
        'naziv_objekta': naplatni_uredjaj.organizaciona_jedinica.efi_kod,
        'adresa_objekta': naplatni_uredjaj.organizaciona_jedinica.puna_adresa,
        'enu_kod': naplatni_uredjaj.efi_kod,

        'datum_dokumenta': now.date(),
        'vrijeme_dokumenta': now.time(),
        'kod_operatera': operater.kodoperatera,
        'report_type': report_type,
        'naslov': REPORT_TITLE_BY_TYPE[report_type],

        'gotovina_u_enu': gotovina_u_enu,
        'inicijalni_depozit': inicijalni_depozit,
        'podignuta_gotovina': podignuta_gotovina,

        'gotovinski_promet_cijena': gotovinski_promet_cijena,
        'gotovinski_promet_popust': gotovinski_promet_popust,
        'gotovinski_promet_za_uplatu': gotovinski_promet_za_uplatu,
        'gotovinski_promet_novcanice': gotovinski_promet_novcanice,
        'gotovinski_promet_kreditna_kartica': gotovinski_promet_kreditna_kartica,
        'gotovinski_promet_order': gotovinski_promet_order,
        'gotovina_cijena_prodajna_ostalo': gotovina_cijena_prodajna_ostalo,
        'gotovinski_promet_bez_novcanica': gotovinski_promet_bez_novcanica,

        'bezgotovinski_cijena_puna': bezgotovinski_cijena_puna,
        'bezgotovinski_popust': bezgotovinski_popust,
        'bezgotovinski_cijena_prodajna': bezgotovinski_cijena_prodajna,

        'bezgotovinski_vrsta_virman': bezgotovinski_vrsta_virman,
        'bezgotovinski_vrsta_biznis_kred_kartica': bezgotovinski_vrsta_biznis_kred_kartica,
        'bezgotovinski_vrsta_jednokratni_vaucer': bezgotovinski_vrsta_jednokratni_vaucer,
        'bezgotovinski_vrsta_kartica_prodavca': bezgotovinski_vrsta_kartica_prodavca,
        'bezgotovinski_vrsta_order': bezgotovinski_vrsta_order,
        'bezgotovinski_vrsta_avans': bezgotovinski_vrsta_avans,
        'bezgotovinski_vrsta_faktoring': bezgotovinski_vrsta_faktoring,
        'bezgotovinski_vrsta_ostalo': bezgotovinski_promet_ostalo,

        'ukupno_prodajna_cijena': ukupno_prodajna_cijena,
        'ukupno_puna_cijena': ukupno_puna_cijena,
        'ukupno_popust': ukupno_popust,

        'korektivni_racuni_broj': korektivni_racun_broj,
        'korektivni_racuni_promet': korektivni_racun_promet,
        'korektivni_racuni_porez': korektivni_racun_porez,

        'offline_racuni_broj': 0.00,
        'offline_racuni_promet': 0.00,
        'offline_racuni_porez': 0.00,

        'order_racuni_broj': 0.00,
        'order_racuni_promet': 0.00,
        'order_racuni_porez': 0.00,

        'poreska_stopa_21_osnovica': poreska_stopa_21_osnovica,
        'poreska_stopa_21_iznos_poreza': poreska_stopa_21_iznos_poreza,
        'poreska_stopa_21_promet': poreska_stopa_21_promet,

        'poreska_stopa_7_osnovica': poreska_stopa_7_osnovica,
        'poreska_stopa_7_iznos_poreza': poreska_stopa_7_iznos_poreza,
        'poreska_stopa_7_promet': poreska_stopa_7_promet,

        'poreska_stopa_0_osnovica': poreska_stopa_0_osnovica,
        'poreska_stopa_0_iznos_poreza': poreska_stopa_0_iznos_poreza,
        'poreska_stopa_0_promet': poreska_stopa_0_promet,

        'ukupan_porez_osnovica': ukupan_porez_osnovica,
        'ukupan_porez_iznos': ukupan_porez_iznos,
        'ukupan_porez_promet': ukupan_porez_promet,

        'oslobodjeni_promet': oslobodjeni_promet
    }

    logger.info("Report finished", extra={
        'report_data': result
    })

    return result


def izvjestaj_po_grupama_artikala(naplatni_uredjaj_id, datum_od, datum_do):
    invoice_types = [
        Faktura.TYPE_REGULAR,
        Faktura.TYPE_CANCELLATION,
        Faktura.TYPE_CORRECTIVE]

    invoice_statuses = [
        Faktura.STATUS_FISCALISATION_SUCCESS,
        Faktura.STATUS_CANCELLED]

    return db.session.query(
        GrupaArtikala.id.label('grupa_artikala_id'),
        GrupaArtikala.naziv.label('grupa_artikala_naziv'),
        func.sum(FakturaStavka.ukupna_cijena_prodajna).label('ukupna_cijena_prodajna'),
        func.sum(FakturaStavka.kolicina).label('kolicina')) \
        .join(Faktura, Faktura.id == FakturaStavka.faktura_id) \
        .join(MagacinZaliha, MagacinZaliha.id == FakturaStavka.magacin_zaliha_id) \
        .join(Artikal, Artikal.id == MagacinZaliha.artikal_id) \
        .join(GrupaArtikala, GrupaArtikala.id == Artikal.grupa_artikala_id) \
        .filter(Faktura.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(Faktura.datumfakture >= datum_od) \
        .filter(Faktura.datumfakture <= datum_do) \
        .filter(Faktura.status.in_(invoice_statuses)) \
        .filter(Faktura.tip_fakture_id.in_(invoice_types)) \
        .filter(Faktura.storno_faktura_id.is_(None)) \
        .group_by(GrupaArtikala.id, GrupaArtikala.naziv) \
        .all()


def izvjestaj_po_artiklima(
        naplatni_uredjaj_id: int,
        datum_od: datetime,
        datum_do: datetime,
        buyer: t.Optional[Komitent] = None
):
    invoice_types = [
        Faktura.TYPE_REGULAR,
        Faktura.TYPE_CANCELLATION,
        Faktura.TYPE_CORRECTIVE
    ]

    invoice_statuses = [
        Faktura.STATUS_FISCALISATION_SUCCESS,
        Faktura.STATUS_CANCELLED,
        Faktura.STATUS_IN_CREDIT_NOTE
    ]

    query = db.session.query(
        Artikal.sifra.label('artikal_sifra'),
        Artikal.id.label('artikal_id'),
        Artikal.naziv.label('artikal_naziv'),
        func.sum(FakturaStavka.ukupna_cijena_prodajna).label('ukupna_cijena_prodajna'),
        func.sum(FakturaStavka.kolicina).label('kolicina')) \
        .join(Faktura, Faktura.id == FakturaStavka.faktura_id) \
        .join(MagacinZaliha, MagacinZaliha.id == FakturaStavka.magacin_zaliha_id) \
        .join(Artikal, Artikal.id == MagacinZaliha.artikal_id) \
        .filter(Faktura.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(Faktura.datumfakture >= datum_od) \
        .filter(Faktura.datumfakture <= datum_do) \
        .filter(Faktura.status.in_(invoice_statuses)) \
        .filter(Faktura.tip_fakture_id.in_(invoice_types)) \
        .filter(Faktura.storno_faktura_id.is_(None)) \
        .group_by(Artikal.id, Artikal.naziv, Artikal.sifra)

    if buyer is not None:
        query = query.filter(Faktura.komitent_id == buyer.id)

    return query.all()
