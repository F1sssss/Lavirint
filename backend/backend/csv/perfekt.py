import csv
import os
import traceback
from datetime import datetime
from pathlib import Path

from _decimal import Decimal

from backend import i18n
from backend.db import db
from backend.csv import parsing
from backend.csv.parsing import Errors
from backend.csv.parsing import Fields
from backend.csv.parsing import ParseException
from backend.models import CsvDatoteka
from backend.models import CsvObrada
from backend.models import JedinicaMjere
from backend.models import Komitent
from backend.opb import csv_opb, operater_opb
from backend.opb import faktura_opb
from backend.opb import firma_opb
from backend.opb import komitent_opb
from backend.opb import misc_opb


def pokreni_obradu(csv_obrada_id):
    csv_obrada = db.session.query(CsvObrada).get(csv_obrada_id)

    if csv_obrada is None:
        raise ParseException('Obrada sa ID-ed %s ne postoji' % csv_obrada_id)

    broj_datoteka = 0
    for putanja_datoteke in Path(csv_obrada.lokacija_ulaznih_csv_datoteka).glob('**/*'):
        broj_datoteka += 1

        csv_datoteka = CsvDatoteka()
        csv_datoteka.status = 1
        csv_datoteka.putanja = putanja_datoteke
        csv_datoteka.naziv = putanja_datoteke.name
        db.session.add(csv_datoteka)
        db.session.commit()

        timestamp = datetime.now()

        izlazna_putanja = Path(csv_obrada.lokacija_izlaznih_csv_datoteka, putanja_datoteke.name)
        neuspjela_obrada_putanja = Path(csv_obrada.lokacija_neuspjelih_csv_datoteka, putanja_datoteke.name)
        uspjela_obrada_putanja = Path(csv_obrada.lokacija_uspjelih_csv_datoteka, putanja_datoteke.name)
        debug_putanja = Path(
            csv_obrada.lokacija_debug_datoteka,
            '%s_%s.csv' % (os.path.splitext(putanja_datoteke.name)[0], timestamp.strftime('%Y%m%d%H%M%S'))
        )

        try:
            podaci, firma, operater, naplatni_uredjaj, faktura_za_korekciju = \
                procitaj_fakturu_iz_csv_datoteke(csv_obrada, putanja_datoteke)
        except ParseException as parse_exception:
            data = [
                [0, str(parse_exception)]
            ]

            save_output(izlazna_putanja, data)
            save_debug(debug_putanja, data)
            os.rename(putanja_datoteke, neuspjela_obrada_putanja)
            continue
        except Exception:
            save_output(izlazna_putanja, [
                [0, 'Došlo je do nepoznate greške']
            ])

            save_debug(debug_putanja, [
                [0, traceback.format_exc()]
            ])

            os.rename(putanja_datoteke, neuspjela_obrada_putanja)
            continue

        if faktura_za_korekciju is None:
            result, output_invoice = faktura_opb.make_regular_invoice(
                podaci, firma, operater, naplatni_uredjaj, calculate_totals=False)
        else:
            result, corrective_invoice, _ = \
                faktura_opb.make_cancellation_invoice(faktura_za_korekciju.id, operater, datetime.now())
            output_invoice = corrective_invoice

        if result.is_success:
            data = [
                [
                    1,
                    output_invoice.efi_ordinal_number,
                    output_invoice.efi_broj_fakture,
                    output_invoice.efi_verify_url,
                    output_invoice.ikof,
                    output_invoice.jikr
                ]
            ]
            save_output(izlazna_putanja, data)
            save_debug(debug_putanja, data)
            os.rename(putanja_datoteke, uspjela_obrada_putanja)
        else:
            data = [
                [0, result.get_message(i18n.LOCALE_SR_LATN_ME)]
            ]

            save_output(izlazna_putanja, data)
            save_debug(debug_putanja, data)
            os.rename(putanja_datoteke, neuspjela_obrada_putanja)

    return broj_datoteka


invoice_headers = (
    Fields.INVOICE_SELLER_IDENTIFICATION,
    Fields.INVOICE_TYPE,
    Fields.INVOICE_TYPE_OF_SELFISS,  # TODO: deprecated
    Fields.INVOICE_IS_SIMPLIFIED_INV,  # TODO: deprecated
    Fields.INVOICE_DATE_CREATED,
    'csv_header_5',  # TODO: deprecated
    'csv_header_6',  # TODO: deprecated
    'csv_header_7',  # TODO: deprecated
    Fields.INVOICE_TOTAL_BASE_PRICE,
    Fields.INVOICE_TAX_AMOUNT,
    Fields.INVOICE_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX,
    Fields.INVOICE_OPERATOR_EFI_CODE,
    Fields.INVOICE_TCR_CODE,
    'csv_header_13',  # TODO: deprecated
    'csv_header_14',  # TODO: deprecated
    Fields.INVOICE_CORRECTION_INVOICE_IIC_REFERENCE,
    Fields.INVOICE_TAX_PERIOD,
    Fields.INVOICE_PAYMENT_TYPE_ID,
    'csv_header_18',  # TODO: deprecated
    Fields.INVOICE_CURRENCY_ISO_CODE,
    'csv_header_20',  # TODO: deprecated
    'csv_header_21',  # TODO: deprecated
    'csv_header_22',  # TODO: deprecated
    'csv_header_23',  # TODO: deprecated
    Fields.BUYER_IDENTIFICATION_TYPE_ID,
    Fields.BUYER_IDENTIFICATION_NUMBER,
    Fields.BUYER_NAME,
    Fields.BUYER_ADRESS,
    Fields.BUYER_CITY,
    Fields.BUYER_COUNTRY_CODE,
    Fields.INVOICE_NUMBER_OF_INVOICE_ITEMS
)

item_headers = (
    Fields.ITEM_DESCRIPTION,
    Fields.ITEM_CODE,
    Fields.ITEM_UNIT_OF_MEASURE,
    Fields.ITEM_QUANTITY,
    Fields.ITEM_UNIT_BASE_PRICE,
    Fields.ITEM_UNIT_BASE_PRICE_WITH_TAX_ONLY,
    Fields.ITEM_REBATE_PERCENTAGE,
    Fields.ITEM_TOTAL_BASE_PRICE_WITH_REBATE_ONLY,
    Fields.ITEM_TAX_PERCENTAGE,
    Fields.ITEM_VAT_EXEMPTION_REASON_ID,
    Fields.ITEM_TOTAL_TAX_AMOUNT,
    Fields.ITEM_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX,
    Fields.ITEM_UNIT_BASE_PRICE_WITH_REBATE_ONLY,
    Fields.ITEM_UNIT_BASE_PRICE_WITH_REBATE_AND_TAX,
)


def procitaj_fakturu_iz_csv_datoteke(obrada, filepath):
    with open(filepath) as file:
        reader = csv.reader(file, delimiter=',')
        lines = []
        for line in reader:
            lines.append(line)

    if len(lines) < 2:
        raise ParseException({
            i18n.LOCALE_SR_LATN_ME: 'Datoteka mora imati najmanje 2 linije.',
            i18n.LOCALE_EN_US: 'File must contain at least 2 lines.'
        })

    parser = parsing.Parser(invoice_headers)
    parser.set_headers(invoice_headers, None, check_length=False)  # Header is not contained in file
    parser.set_values(lines.pop(0), 1, check_length=False)
    parser.refresh_record()

    with parser.get_field(Fields.INVOICE_SELLER_IDENTIFICATION) as value:
        _invoice_seller_identification = parsing.to_string_or_none(value)
        parsing.raise_if(value is None, Errors.MISSING_MANDATORY_VALUE)
        parsing.raise_if(len(_invoice_seller_identification) != 8, {
            i18n.LOCALE_SR_LATN_ME: 'Identifikaciona oznaka prodavca mora imati tačno 8 numeričkih znaka.',
            i18n.LOCALE_EN_US: 'Seller identification must be exactly 8 characters long.',
        })

        ovlascenje = csv_opb.listaj_ovlascenje_po_pibu(obrada.id, _invoice_seller_identification)
        parsing.raise_if(ovlascenje is None, {
            i18n.LOCALE_SR_LATN_ME: 'Nema ovlašćenja. Kontaktirajte administratore sistem.',
            i18n.LOCALE_EN_US: 'No authorization. Please contact system administrators.'
        })

    with parser.get_field(Fields.INVOICE_TYPE) as value:
        # _invoice_type = parsing.to_string_or_none(value)
        # parsing.raise_if(_invoice_type is None, Errors.MISSING_MANDATORY_VALUE)
        # parsing.raise_if(faktura_opb.listaj_tip_fakture_po_idu(_invoice_type) is None, {
        #     i18n.LOCALE_SR_LATN_ME: '',  # TODO Adds error description
        #     i18n.LOCALE_EN_US: 'Value of "invoice_type" header on line %s is not a valid invoice type id.'
        #                        % _invoice_type
        # })
        _invoice_type = 1
        pass

    # Podatak se ne koristi
    # TypeOfSelfiss: podaci_fakture[2]

    # Podatak se ne koristi
    # IsSimplifiedInv: podaci_fakture[3]

    with parser.get_field(Fields.INVOICE_DATE_CREATED) as value:
        _invoice_date_created = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_date_created is None)
        _invoice_date_created = parsing.to_datetime(_invoice_date_created, format_='%d.%m.%Y %H:%M:%S')

    # Podatak se ne koristi
    # podaci['redni_broj_racuna'] = csv_header[5]

    # Podatak se ne koristi
    # brojOrderaZaRacun: csv_header[6]

    # Podatak se ne koristi
    # neoporeziniIznos: csv_header[7]

    with parser.get_field(Fields.INVOICE_TOTAL_BASE_PRICE) as value:
        _invoice_total_base_price = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_total_base_price is None, Errors.MISSING_MANDATORY_VALUE)
        _invoice_total_base_price = parsing.to_decimal(_invoice_total_base_price)

    with parser.get_field(Fields.INVOICE_TAX_AMOUNT) as value:
        _porez_iznos = parsing.to_string_or_none(value)
        parsing.raise_if(_porez_iznos is None, Errors.MISSING_MANDATORY_VALUE)
        _porez_iznos = parsing.to_decimal(_porez_iznos)

    with parser.get_field(Fields.INVOICE_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX) as value:
        _ukupna_cijena_prodajna = parsing.to_string_or_none(value)
        parsing.raise_if(_ukupna_cijena_prodajna is None, Errors.MISSING_MANDATORY_VALUE)
        _ukupna_cijena_prodajna = parsing.to_decimal(_ukupna_cijena_prodajna)

    with parser.get_field(Fields.INVOICE_OPERATOR_EFI_CODE) as value:
        _kod_operatera = parsing.to_string_or_none(value)
        parsing.raise_if(_kod_operatera is None, Errors.MISSING_MANDATORY_VALUE)
        operater = operater_opb.get_customer_user_by_efi_code(ovlascenje.firma.id, _kod_operatera)
        parsing.raise_if(operater is None, {
            i18n.LOCALE_SR_LATN_ME: 'Ne postoji operater sa kodom "%s"' % _kod_operatera,
            i18n.LOCALE_EN_US: 'Operator code "%s" does not exist.' % _kod_operatera
        })

    with parser.get_field(Fields.INVOICE_TCR_CODE) as value:
        _kod_naplatnog_uredjaja = parsing.to_string_or_none(value)
        parsing.raise_if(_kod_naplatnog_uredjaja is None, Errors.MISSING_MANDATORY_VALUE)
        _kod_naplatnog_uredjaja = parsing.to_registration_code(_kod_naplatnog_uredjaja)
        naplatni_uredjaj = firma_opb.listaj_naplatni_uredjaj_po_efi_kodu(_kod_naplatnog_uredjaja)
        parsing.raise_if(naplatni_uredjaj is None, 'Ne postoji naplatni uređaj sa kodom "%s"' % _kod_naplatnog_uredjaja)

    # Podatak se ne koristi
    # podaci['datumvalute'] = csv_header[13]  # TODO: Ne postoji podatak

    # Podatak se ne koristi
    # brojParagonBloka: csv_header[14]

    with parser.get_field(Fields.INVOICE_CORRECTION_INVOICE_IIC_REFERENCE) as value:
        faktura_za_korekciju = None
        faktura_za_korekciju_ikof = parsing.to_string_or_none(value)
        if faktura_za_korekciju_ikof is not None:
            faktura_za_korekciju = faktura_opb.listaj_fakturu_po_ikofu(faktura_za_korekciju_ikof)
            parsing.raise_if(
                faktura_za_korekciju is None,
                'Ne postoji faktura sa IKOF-om "%s"' % faktura_za_korekciju_ikof)
            parsing.raise_if(
                faktura_za_korekciju.firma_id != ovlascenje.firma.id,
                'Faktura za korekciju sa IKOF-om "%s" ne pripada navedenoj firmi za PIB-om "%s"'
                % (faktura_za_korekciju_ikof, _invoice_seller_identification))

    with parser.get_field(Fields.INVOICE_TAX_PERIOD) as value:
        _poreski_period = parsing.to_string_or_none(value)
        if _poreski_period is None:
            _poreski_period = datetime.now().strftime('%m/%Y')
        _poreski_period = parsing.to_tax_period(_poreski_period)

    with parser.get_field(Fields.INVOICE_PAYMENT_TYPE_ID) as value:
        _vrstaplacanja_id = parsing.to_string_or_none(value)
        parsing.raise_if(_vrstaplacanja_id is None, Errors.MISSING_MANDATORY_VALUE)
        _vrstaplacanja = faktura_opb.get_payment_method_type_by_id(_vrstaplacanja_id)
        parsing.raise_if(_vrstaplacanja is None, 'Vrijednost vrste plaćanja nije ispravna vrijednost')

    # Podatak se ne koristi
    # iznosPlacanja: csv_header[18]

    with parser.get_field(Fields.INVOICE_CURRENCY_ISO_CODE) as value:
        _kod_valute = parsing.to_string_or_none(value)
        parsing.raise_if(_kod_valute is None, Errors.MISSING_MANDATORY_VALUE)
        _valuta = misc_opb.listaj_valutu_po_iso_kodu(_kod_valute)
        parsing.raise_if(_valuta is None, 'Kod valute nije ispravna vrijednost')

    # Poslovna jedinica se ne čita iz CSV datoteke već se preuzima
    # po naplatnom uređaju

    # Podatak se ne koristi
    # poslovna_jedinica_kod = csv_header[20]

    # Podatak se ne koristi
    # poslovna_jedinica_adresa: csv_header[21]

    # Podatak se ne koristi
    # poslovna_jedinica_grad: csv_header[22]

    # Podatak se ne koristi
    # poslovna_jedinica_drzava: csv_header[23]

    with parser.get_field(Fields.BUYER_IDENTIFICATION_TYPE_ID) as value:
        kupac_tip_id_oznake = parsing.to_string_or_none(value)

    with parser.get_field(Fields.BUYER_IDENTIFICATION_NUMBER) as value:
        kupac_id_oznaka = parsing.to_string_or_none(value)

    _komitent_id = None
    if kupac_id_oznaka not in ('0', '-1', None) and kupac_tip_id_oznake not in ('0', '-1', None):  # TODO
        kupac_tip_id_oznake = parsing.to_integer(kupac_tip_id_oznake)
        parsing.raise_if(
            kupac_tip_id_oznake == 1 and len(kupac_id_oznaka) != 13,
            'Identifikaciona oznaka nije ispravnog formata')
        parsing.raise_if(
            kupac_tip_id_oznake == 2 and len(kupac_id_oznaka) != 8,
            'Identifikaciona oznaka nije ispravnog formata')

        with parser.get_field(Fields.BUYER_NAME) as value:
            kupac_naziv = parsing.to_string_or_none(value)
            parsing.raise_if(kupac_naziv is None, Errors.MISSING_MANDATORY_VALUE)

        with parser.get_field(Fields.BUYER_ADRESS) as value:
            komitent_adresa = parsing.to_string_or_none(value)
            parsing.raise_if(komitent_adresa is None, Errors.MISSING_MANDATORY_VALUE)

        with parser.get_field(Fields.BUYER_CITY) as value:
            komitent_grad = parsing.to_string_or_none(value)
            parsing.raise_if(komitent_grad is None, Errors.MISSING_MANDATORY_VALUE)

        komitent = komitent_opb.po_identifikaciji__listaj(
            kupac_tip_id_oznake, kupac_id_oznaka, ovlascenje.firma.pib
        )
        if komitent is None:
            komitent = Komitent()
            komitent.tip_identifikacione_oznake_id = kupac_tip_id_oznake
            komitent.identifikaciona_oznaka = kupac_id_oznaka
            komitent.pibvlasnikapodatka = ovlascenje.firma.pib
            komitent.naziv = kupac_naziv
            komitent.adresa = komitent_adresa
            komitent.grad = komitent_grad
            komitent.drzava = 39  # TODO: Drzava je fiksirana
            db.session.add(komitent)
            db.session.commit()
        else:
            if komitent.tip_identifikacione_oznake_id != kupac_tip_id_oznake:
                komitent.tip_identifikacione_oznake_id = kupac_tip_id_oznake
            if komitent.identifikaciona_oznaka != kupac_id_oznaka:
                komitent.identifikaciona_oznaka = kupac_id_oznaka
            if komitent.naziv != kupac_naziv:
                komitent.naziv = kupac_naziv
            if komitent.adresa != komitent_adresa:
                komitent.adresa = komitent_adresa
            if komitent.grad != komitent_grad:
                komitent.grad = komitent_grad
            db.session.add(komitent)
            db.session.commit()

        _komitent_id = komitent.id

    podaci = {
        'stavke': [],
        'tip_fakture': _invoice_type,
        'datumfakture': _invoice_date_created,
        'ukupna_cijena_osnovna': _invoice_total_base_price,
        'porez_iznos': _porez_iznos,
        'ukupna_cijena_prodajna': _ukupna_cijena_prodajna,
        'datumvalute': _invoice_date_created,
        'poreski_period': _poreski_period,
        'is_cash': _vrstaplacanja.is_cash,
        'payment_methods': [{
            'payment_method_type_id': _vrstaplacanja.id
        }],
        'valuta_id': _valuta.id,
        'kurs_razmjene': 1,
        'komitent_id': _komitent_id
    }

    parser = parsing.Parser(item_headers)
    parser.set_headers(item_headers, None, check_length=False)  # Header is not contained in file

    for index, row in enumerate(lines):
        parser.set_values(row, line_number=index + 1 + 1, check_length=False)
        parser.refresh_record()

        with parser.get_field(Fields.ITEM_DESCRIPTION) as value:
            stavka_naziv = parsing.to_string_or_none(value)
            parsing.raise_if(stavka_naziv is None, Errors.MISSING_MANDATORY_VALUE)

        with parser.get_field(Fields.ITEM_CODE) as value:
            stavka_sifra = parsing.to_string_or_none(value)

        with parser.get_field(Fields.ITEM_UNIT_OF_MEASURE) as value:
            jedinica_mjere_naziv = parsing.to_string_or_none(value)
            parsing.raise_if(jedinica_mjere_naziv is None, Errors.MISSING_MANDATORY_VALUE)
            jedinica_mjere = misc_opb.listaj_jedinicu_mjere_po_nazivu(ovlascenje.firma.id, jedinica_mjere_naziv)
            if jedinica_mjere is None:
                jedinica_mjere = JedinicaMjere()
                jedinica_mjere.naziv = jedinica_mjere_naziv
                jedinica_mjere.firma = ovlascenje.firma
                jedinica_mjere.opis = jedinica_mjere_naziv
                jedinica_mjere.ui_default = False
                db.session.add(jedinica_mjere)
                db.session.commit()

        with parser.get_field(Fields.ITEM_QUANTITY) as value:
            stavka_kolicina = parsing.to_string_or_none(value)
            parsing.raise_if(stavka_kolicina is None, Errors.MISSING_MANDATORY_VALUE)
            stavka_kolicina = parsing.to_decimal(stavka_kolicina)

        with parser.get_field(Fields.ITEM_UNIT_BASE_PRICE) as value:
            stavka_jedinicna_cijena_osnovna = parsing.to_string_or_none(value)
            parsing.raise_if(stavka_jedinicna_cijena_osnovna is None, Errors.MISSING_MANDATORY_VALUE)
            stavka_jedinicna_cijena_osnovna = parsing.to_decimal(stavka_jedinicna_cijena_osnovna)

        with parser.get_field(Fields.ITEM_UNIT_BASE_PRICE_WITH_TAX_ONLY) as value:
            stavka_jedinicna_cijena_puna = parsing.to_string_or_none(value)
            parsing.raise_if(stavka_jedinicna_cijena_puna is None, Errors.MISSING_MANDATORY_VALUE)
            stavka_jedinicna_cijena_puna = parsing.to_decimal(stavka_jedinicna_cijena_puna)

        with parser.get_field(Fields.ITEM_REBATE_PERCENTAGE) as value:
            stavka_rabat_procenat = parsing.to_string_or_none(value)
            parsing.raise_if(stavka_rabat_procenat is None, Errors.MISSING_MANDATORY_VALUE)
            stavka_rabat_procenat = parsing.to_decimal(stavka_rabat_procenat)

        with parser.get_field(Fields.ITEM_UNIT_BASE_PRICE_WITH_REBATE_ONLY) as value:
            stavka_jedinicna_cijena_rabatisana = parsing.to_string_or_none(value)
            parsing.raise_if(stavka_jedinicna_cijena_rabatisana is None, Errors.MISSING_MANDATORY_VALUE)
            stavka_jedinicna_cijena_rabatisana = parsing.to_decimal(stavka_jedinicna_cijena_rabatisana)

        with parser.get_field(Fields.ITEM_UNIT_BASE_PRICE_WITH_REBATE_AND_TAX) as value:
            stavka_jedinicna_cijena_prodajna = parsing.to_string_or_none(value)
            parsing.raise_if(stavka_jedinicna_cijena_prodajna is None, Errors.MISSING_MANDATORY_VALUE)
            stavka_jedinicna_cijena_prodajna = parsing.to_decimal(stavka_jedinicna_cijena_prodajna)

        with parser.get_field(Fields.ITEM_TOTAL_BASE_PRICE_WITH_REBATE_ONLY) as value:
            stavka_ukupna_cijena_rabatisana = parsing.to_string_or_none(row[7])
            parsing.raise_if(stavka_ukupna_cijena_rabatisana is None, Errors.MISSING_MANDATORY_VALUE)
            stavka_ukupna_cijena_rabatisana = parsing.to_decimal(stavka_ukupna_cijena_rabatisana)

        with parser.get_field(Fields.ITEM_TAX_PERCENTAGE) as value:
            stavka_porez_procenat = parsing.to_string_or_none(value)
            if stavka_porez_procenat is not None:
                stavka_porez_procenat = parsing.to_decimal(stavka_porez_procenat)

        with parser.get_field(Fields.ITEM_VAT_EXEMPTION_REASON_ID) as value:
            tax_exemption_reason_id = parsing.to_string_or_none(value)
            if tax_exemption_reason_id is None:
                if stavka_porez_procenat is None:
                    parsing.raise_if(tax_exemption_reason_id is None, Errors.MISSING_MANDATORY_VALUE)
            else:
                # TODO Check if tax is set to anything other than 0 or None and raise error
                tax_exemption_reason_id = parsing.to_integer(tax_exemption_reason_id)

        with parser.get_field(Fields.ITEM_TOTAL_TAX_AMOUNT) as value:
            stavka_porez_iznos = parsing.to_string_or_none(value)
            parsing.raise_if(stavka_porez_iznos is None, Errors.MISSING_MANDATORY_VALUE)
            stavka_porez_iznos = parsing.to_decimal(stavka_porez_iznos)

        with parser.get_field(Fields.ITEM_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX) as value:
            stavka_ukupna_cijena_prodajna = parsing.to_string_or_none(value)
            parsing.raise_if(stavka_ukupna_cijena_prodajna is None, Errors.MISSING_MANDATORY_VALUE)
            stavka_ukupna_cijena_prodajna = parsing.to_decimal(stavka_ukupna_cijena_prodajna)

        # Calculated values
        stavka_ukupna_cijena_puna = stavka_jedinicna_cijena_puna * stavka_kolicina
        stavka_ukupna_cijena_osnovna = stavka_jedinicna_cijena_osnovna * stavka_kolicina
        stavka_rabat_iznos_osnovni = stavka_ukupna_cijena_osnovna * (stavka_rabat_procenat / 100)
        stavka_rabat_iznos_prodajni = stavka_ukupna_cijena_prodajna * (stavka_rabat_procenat / 100)

        podaci['stavke'].append({
            'izvor_kalkulacije': 2,
            'naziv': stavka_naziv,
            'sifra': stavka_sifra,
            'jedinica_mjere_id': jedinica_mjere.id,
            'kolicina': stavka_kolicina,
            'jedinicna_cijena_osnovna': stavka_jedinicna_cijena_osnovna,
            'rabat_procenat': stavka_rabat_procenat,
            'jedinicna_cijena_puna': stavka_jedinicna_cijena_puna,
            'jedinicna_cijena_rabatisana': stavka_jedinicna_cijena_rabatisana,
            'jedinicna_cijena_prodajna': stavka_jedinicna_cijena_prodajna,
            'ukupna_cijena_osnovna': stavka_ukupna_cijena_osnovna,
            'ukupna_cijena_rabatisana': stavka_ukupna_cijena_rabatisana,
            'ukupna_cijena_puna': stavka_ukupna_cijena_puna,
            'ukupna_cijena_prodajna': stavka_ukupna_cijena_prodajna,
            'porez_procenat': stavka_porez_procenat,
            'tax_exemption_reason_id': tax_exemption_reason_id,
            'tax_exemption_amount': 0 if tax_exemption_reason_id is None else stavka_ukupna_cijena_prodajna,
            'porez_iznos': stavka_porez_iznos,
            'rabat_iznos_osnovni': stavka_rabat_iznos_osnovni,
            'rabat_iznos_prodajni': stavka_rabat_iznos_prodajni
        })

    podaci['ukupna_cijena_rabatisana'] = 0
    podaci['ukupna_cijena_puna'] = 0
    podaci['rabat_iznos_osnovni'] = 0
    podaci['rabat_iznos_prodajni'] = 0
    podaci['tax_exemption_amount'] = 0
    for stavka in podaci['stavke']:
        podaci['ukupna_cijena_puna'] += stavka['ukupna_cijena_puna']
        podaci['ukupna_cijena_rabatisana'] += stavka['ukupna_cijena_rabatisana']
        podaci['rabat_iznos_osnovni'] += stavka['rabat_iznos_osnovni']
        podaci['rabat_iznos_prodajni'] += stavka['rabat_iznos_prodajni']
        podaci['tax_exemption_amount'] += stavka['tax_exemption_amount']

    # ------------------------------------------------------------------------------------------------------------------
    # TODO Refactor
    podaci['tax_exemption_amount'] = Decimal(0)
    for stavka in podaci['stavke']:
        if stavka['tax_exemption_reason_id'] is not None:
            podaci['tax_exemption_amount'] += Decimal(stavka['tax_exemption_amount'])
    # ------------------------------------------------------------------------------------------------------------------

    return podaci, ovlascenje.firma, operater, naplatni_uredjaj, faktura_za_korekciju


def save_debug(filepath, lines):
    with open(filepath, 'w') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        writer.writerows(lines)


def save_output(filepath, lines):
    with open(filepath, 'w') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        writer.writerows(lines)
