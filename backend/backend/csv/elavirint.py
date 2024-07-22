import csv
import os
import traceback
from datetime import datetime
from pathlib import Path

from _decimal import Decimal

from backend import i18n
from backend.db import db
from backend.csv import parsing
from backend.models import CsvDatoteka
from backend.models import JedinicaMjere
from backend.models import Komitent
from backend.opb import csv_opb, operater_opb
from backend.opb import faktura_opb
from backend.opb import firma_opb
from backend.opb import helpers
from backend.opb import komitent_opb
from backend.opb import misc_opb

invoice_headers = (
    parsing.Fields.INVOICE_SELLER_IDENTIFICATION,
    parsing.Fields.INVOICE_TCR_CODE,
    parsing.Fields.INVOICE_TYPE,
    parsing.Fields.INVOICE_DATE_CREATED,
    parsing.Fields.INVOICE_VALUE_DATE,
    parsing.Fields.INVOICE_TAX_PERIOD,
    parsing.Fields.INVOICE_PAYMENT_TYPE_ID,
    parsing.Fields.INVOICE_OPERATOR_EFI_CODE,
    parsing.Fields.INVOICE_TOTAL_BASE_PRICE,
    parsing.Fields.INVOICE_TOTAL_BASE_PRICE_WITH_REBATE_ONLY,
    parsing.Fields.INVOICE_TOTAL_BASE_PRICE_WITH_TAX_ONLY,
    parsing.Fields.INVOICE_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX,
    parsing.Fields.INVOICE_TAX_AMOUNT,
    parsing.Fields.INVOICE_REBATE_AMOUNT_BEFORE_VAT,
    parsing.Fields.INVOICE_REBATE_AMOUNT_AFTER_VAT,
    parsing.Fields.INVOICE_CORRECTION_INVOICE_IIC_REFERENCE,
    parsing.Fields.INVOICE_CURRENCY_ISO_CODE,
    parsing.Fields.INVOICE_CURRENCT_EXCHANGE_RATE,
    parsing.Fields.INVOICE_NOTE,
    parsing.Fields.INVOICE_HAS_BUYER,
    parsing.Fields.INVOICE_NUMBER_OF_INVOICE_ITEMS,
    parsing.Fields.INVOICE_NUMBER_OF_TAX_ITEMS,
)

expected_buyer_headers = (
    parsing.Fields.BUYER_IDENTIFICATION_TYPE_ID,
    parsing.Fields.BUYER_IDENTIFICATION_NUMBER,
    parsing.Fields.BUYER_NAME,
    parsing.Fields.BUYER_ADRESS,
    parsing.Fields.BUYER_CITY,
    parsing.Fields.BUYER_COUNTRY_CODE,
)

expected_invoice_item_headers = (
    parsing.Fields.ITEM_CODE,
    parsing.Fields.ITEM_DESCRIPTION,
    parsing.Fields.ITEM_UNIT_BASE_PRICE,
    parsing.Fields.ITEM_REBATE_PERCENTAGE,
    parsing.Fields.ITEM_TAX_PERCENTAGE,
    parsing.Fields.ITEM_UNIT_BASE_PRICE_WITH_REBATE_ONLY,
    parsing.Fields.ITEM_UNIT_BASE_PRICE_WITH_TAX_ONLY,
    parsing.Fields.ITEM_UNIT_BASE_PRICE_WITH_REBATE_AND_TAX,
    parsing.Fields.ITEM_UNIT_OF_MEASURE,
    parsing.Fields.ITEM_QUANTITY,
    parsing.Fields.ITEM_TOTAL_BASE_PRICE,
    parsing.Fields.ITEM_TOTAL_BASE_PRICE_WITH_REBATE_ONLY,
    parsing.Fields.ITEM_TOTAL_BASE_PRICE_WITH_TAX_ONLY,
    parsing.Fields.ITEM_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX,
    parsing.Fields.ITEM_TOTAL_TAX_AMOUNT,
    parsing.Fields.ITEM_TOTAL_REBATE_AMOUNT_BEFORE_VAT,
    parsing.Fields.ITEM_TOTAL_REBATE_AMOUNT_AFTER_VAT,
    parsing.Fields.ITEM_VAT_EXEMPTION_REASON_ID,
)


expected_sametax_item_headers = (
    parsing.Fields.TAX_GROUP_NUMBER_OF_MATCHED_INVOICE_ITEMS,
    parsing.Fields.TAX_GROUP_BASE_PRICE,
    parsing.Fields.TAX_GROUP_BASE_PRICE_WITH_REBATE,
    parsing.Fields.TAX_GROUP_BASE_PRICE_WITH_TAX,
    parsing.Fields.TAX_GROUP_BASE_PRICE_WITH_REBATE_AND_TAX,
    parsing.Fields.TAX_GROUP_TAX_PERCENTAGE,
    parsing.Fields.TAX_GROUP_TAX_AMOUNT,
    parsing.Fields.TAX_GROUP_REBATE_AMOUNT_BEFORE_VAT,
    parsing.Fields.TAX_GROUP_REBATE_AMOUNT_AFTER_VAT,
)


def pokreni_obradu(csv_obrada_id):
    obrada = csv_opb.listaj_obradu_po_idu(csv_obrada_id)

    timestamp = datetime.now()

    if obrada is None:
        raise parsing.ParseException('Obrada sa ID-ed %s ne postoji' % csv_obrada_id)

    broj_datoteka = 0
    for input_filepath in Path(obrada.lokacija_ulaznih_csv_datoteka).glob('**/*'):
        broj_datoteka += 1

        csv_datoteka = CsvDatoteka()
        csv_datoteka.status = 1
        csv_datoteka.putanja = input_filepath
        csv_datoteka.naziv = input_filepath.name
        db.session.add(csv_datoteka)
        db.session.commit()

        output_filepath = Path(obrada.lokacija_izlaznih_csv_datoteka, input_filepath.name)
        fail_filepath = Path(obrada.lokacija_neuspjelih_csv_datoteka, input_filepath.name)
        success_filepath = Path(obrada.lokacija_uspjelih_csv_datoteka, input_filepath.name)
        debug_filepath = Path(
            obrada.lokacija_debug_datoteka,
            '%s_%s.csv' % (os.path.splitext(input_filepath.name)[0], timestamp.strftime('%Y%m%d%H%M%S'))
        )

        try:
            podaci, firma, operater, naplatni_uredjaj, faktura_za_korekciju = \
                load_invoice_csv(obrada, input_filepath)
        except parsing.ParseException as parse_exception:
            lines = create_output_from_invoice(
                input_filepath=input_filepath,
                invoice=None,
                faultcode=100,
                faultstring=str(parse_exception)
            )

            save_output(output_filepath, lines)

            with open(debug_filepath, 'w', encoding='UTF8') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(['is_success', 'description'])
                csv_writer.writerow([0, str(parse_exception)])
            os.rename(input_filepath, fail_filepath)
            continue
        except Exception:
            lines = create_output_from_invoice(
                input_filepath=input_filepath,
                invoice=None,
                faultcode=101,
                faultstring='Unknown error during CSV processing.'
            )

            save_output(output_filepath, lines)

            save_debug(debug_filepath, [
                ['is_success', 'description'],
                [0, traceback.format_exc()]
            ])

            os.rename(input_filepath, fail_filepath)
            continue

        if faktura_za_korekciju is None:
            result, output_invoice = faktura_opb.make_regular_invoice(
                podaci, firma, operater, naplatni_uredjaj, calculate_totals=False)
        else:
            result, corrective_invoice, _ = \
                faktura_opb.make_cancellation_invoice(faktura_za_korekciju.id, operater, datetime.now())
            output_invoice = corrective_invoice

        if result.is_success:
            lines = create_output_from_invoice(
                input_filepath=input_filepath,
                invoice=output_invoice,
                faultcode=None,
                faultstring=None
            )

            # Is success
            save_output(output_filepath, lines)
            os.rename(input_filepath, success_filepath)
            save_debug(debug_filepath, [
                [
                    'is_sucess',
                    'invoice_efi_number',
                    'invoice_efi_verify_url',
                    'invoice_iic_number',
                    'invoice_fic_number',
                ],
                [
                    1,
                    output_invoice.efi_ordinal_number,
                    output_invoice.efi_broj_fakture,
                    output_invoice.efi_verify_url,
                    output_invoice.ikof,
                    output_invoice.jikr
                ]
            ])
        else:
            lines = create_output_from_invoice(
                input_filepath=input_filepath,
                invoice=output_invoice,
                faultcode=None,
                faultstring=result.get_message(i18n.LOCALE_EN_US)
            )
            save_output(output_filepath, lines)
            os.rename(input_filepath, fail_filepath)

    return broj_datoteka


def save_debug(filepath, rows):
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def check_header(actual_values, expected_values):
    if actual_values != expected_values:
        raise parsing.ParseException('Invalid header values.')


def check_record_length(actual_values, expected_length):
    actual_length = len(actual_values)
    if actual_length != expected_length:
        raise parsing.ParseException({
            i18n.LOCALE_SR_LATN_ME:
                'Dužina reda nije ispravna. Očekivana dužina %s, stvarna dužina %s.' % (expected_length, actual_length),
            i18n.LOCALE_EN_US:
                'Invalid record length. Expected %s, got %s values.' % (expected_length, actual_length)
        })


def load_invoice_csv(provider, filepath):

    with open(filepath) as file:
        lines = []
        for line in csv.reader(file, delimiter=','):
            lines.append(line)

    total_lines = len(lines)

    if len(lines) < 8:
        raise parsing.ParseException({
            i18n.LOCALE_SR_LATN_ME: 'Datoteka mora imati najmanje 8 linija.',
            i18n.LOCALE_EN_US: 'File must contain at least 8 lines.'
        })

    parser = parsing.Parser(invoice_headers)
    parser.set_headers(tuple(lines.pop(0)), total_lines - len(lines))
    parser.set_values(lines.pop(0), total_lines - len(lines))
    parser.refresh_record()

    with parser.get_field(parsing.Fields.INVOICE_SELLER_IDENTIFICATION) as value:
        _invoice_seller_identification = parsing.to_string_or_none(value)
        parsing.raise_if(value is None, {
            i18n.LOCALE_SR_LATN_ME: 'Nedostaje identifikacija prodavca.',
            i18n.LOCALE_EN_US: 'Seller identification number is missing.'
        })
        parsing.raise_if(len(value) != 8, {
            i18n.LOCALE_SR_LATN_ME: 'Identifikaciona oznaka prodavca mora imati tačno 8 numeričkih znaka.',
            i18n.LOCALE_EN_US: 'Seller identification must be exactly 8 characters long.',
        })

        ovlascenje = csv_opb.listaj_ovlascenje_po_pibu(provider.id, _invoice_seller_identification)
        parsing.raise_if(ovlascenje is None, {
            i18n.LOCALE_SR_LATN_ME: 'Nema ovlašćenja. Kontaktirajte administratore sistem.',
            i18n.LOCALE_EN_US: 'No authorization. Please contact system administrators.'
        })

    with parser.get_field(parsing.Fields.INVOICE_TYPE) as value:
        _invoice_type = parsing.to_string_or_none(value)
        parsing.raise_if(value is None)
        parsing.raise_if(
            faktura_opb.listaj_tip_fakture_po_idu(_invoice_type) is None,
            'Value of "invoice_type" header on line %s is not a valid invoice type id.' % _invoice_type)

    with parser.get_field(parsing.Fields.INVOICE_DATE_CREATED) as value:
        _invoice_date_created = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_date_created is None)
        _invoice_date_created = parsing.to_datetime(_invoice_date_created)

    with parser.get_field(parsing.Fields.INVOICE_TOTAL_BASE_PRICE) as value:
        _invoice_total_base_price = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_total_base_price is None)
        _invoice_total_base_price = parsing.to_decimal(_invoice_total_base_price)

    with parser.get_field(parsing.Fields.INVOICE_TOTAL_BASE_PRICE_WITH_REBATE_ONLY) as value:
        _invoice_total_base_price_with_rebate_only = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_total_base_price_with_rebate_only is None)
        _invoice_total_base_price_with_rebate_only = parsing.to_decimal(_invoice_total_base_price_with_rebate_only)

    with parser.get_field(parsing.Fields.INVOICE_TOTAL_BASE_PRICE_WITH_TAX_ONLY) as value:
        _invoice_total_base_price_with_tax_only = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_total_base_price_with_tax_only is None)
        _invoice_total_base_price_with_tax_only = parsing.to_decimal(_invoice_total_base_price_with_tax_only)

    with parser.get_field(parsing.Fields.INVOICE_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX) as value:
        _invoice_total_base_price_with_tax_and_rebate = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_total_base_price_with_tax_and_rebate is None)
        _invoice_total_base_price_with_tax_and_rebate = \
            parsing.to_decimal(_invoice_total_base_price_with_tax_and_rebate)

    with parser.get_field(parsing.Fields.INVOICE_TAX_AMOUNT) as value:
        _invoice_tax_amount = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_tax_amount is None)
        _invoice_tax_amount = parsing.to_decimal(_invoice_tax_amount)

    with parser.get_field(parsing.Fields.INVOICE_REBATE_AMOUNT_BEFORE_VAT) as value:
        _invoice_rebate_amount_before_vat = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_rebate_amount_before_vat is None)
        _invoice_rebate_amount_before_vat = parsing.to_decimal(_invoice_rebate_amount_before_vat)

    with parser.get_field(parsing.Fields.INVOICE_REBATE_AMOUNT_AFTER_VAT) as value:
        _invoice_rebate_amount_after_vat = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_rebate_amount_after_vat is None)
        _invoice_rebate_amount_after_vat = parsing.to_decimal(_invoice_rebate_amount_after_vat)

    with parser.get_field(parsing.Fields.INVOICE_OPERATOR_EFI_CODE) as value:
        _invoice_operator_efi_code = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_operator_efi_code is None)
        _invoice_operator_efi_code = parsing.to_registration_code(_invoice_operator_efi_code)
        operater = operater_opb.get_customer_user_by_efi_code(ovlascenje.firma.id, _invoice_operator_efi_code)
        parsing.raise_if(operater is None, 'Invalid operator code %s.' % _invoice_operator_efi_code)

    with parser.get_field(parsing.Fields.INVOICE_TCR_CODE) as value:
        _invoice_tcr_code = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_tcr_code is None)
        _invoice_tcr_code = parsing.to_registration_code(_invoice_tcr_code)
        naplatni_uredjaj = firma_opb.listaj_naplatni_uredjaj_po_efi_kodu(_invoice_tcr_code)
        parsing.raise_if(
            naplatni_uredjaj is None,
            {
                i18n.LOCALE_SR_LATN_ME: 'Unable to find payment device whose code is "%s"' % _invoice_tcr_code,
                i18n.LOCALE_EN_US: 'Unable to find payment device whose code is "%s"' % _invoice_tcr_code
            })

    with parser.get_field(parsing.Fields.INVOICE_VALUE_DATE) as value:
        _invoice_value_date = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_value_date is None)
        _invoice_value_date = parsing.to_datetime(_invoice_value_date)

    with parser.get_field(parsing.Fields.INVOICE_CORRECTION_INVOICE_IIC_REFERENCE) as value:
        faktura_za_korekciju = None
        _corrective_invoice_icc = parsing.to_string_or_none(value)
        if _corrective_invoice_icc is not None:
            faktura_za_korekciju = faktura_opb.listaj_fakturu_po_ikofu(_corrective_invoice_icc)
            parsing.raise_if(
                faktura_za_korekciju is None,
                'Unable to find invoice for correction whose code is "%s".' % _corrective_invoice_icc)
            parsing.raise_if(
                faktura_za_korekciju.firma_id != ovlascenje.firma.id,
                'Unable to find invoice for correction whose code is "%s".' % _corrective_invoice_icc)

    with parser.get_field(parsing.Fields.INVOICE_TAX_PERIOD) as value:
        _invoice_tax_period = parsing.to_string_or_none(value)
        if _invoice_tax_period is not None:
            _invoice_tax_period = parsing.to_tax_period(_invoice_tax_period)

    with parser.get_field(parsing.Fields.INVOICE_PAYMENT_TYPE_ID) as value:
        _invoice_payment_type_id = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_payment_type_id is None)
        _invoice_payment_type_id = parsing.to_integer(_invoice_payment_type_id)
        _invoice_payment_type = faktura_opb.get_payment_method_type_by_id(_invoice_payment_type_id)
        if _invoice_payment_type is None:
            parsing.raise_if(_invoice_payment_type is None, 'Vrijednost vrste plaćanja nije ispravna vrijednost')

    with parser.get_field(parsing.Fields.INVOICE_CURRENCY_ISO_CODE) as value:
        _invoice_currency_iso_code = parsing.to_string_or_none(value)
        parsing.raise_if(_invoice_currency_iso_code is None)
        _db_currency = misc_opb.listaj_valutu_po_iso_kodu(_invoice_currency_iso_code)
        parsing.raise_if(_db_currency is None, 'Currencty ISO code is not valid.')

    if _db_currency.iso_4217_alfanumericki_kod == 'EUR':
        _kurs_razmjene = 1
    else:
        with parser.get_field(parsing.Fields.INVOICE_CURRENCT_EXCHANGE_RATE) as value:
            _kurs_razmjene = parsing.to_string_or_none(value)
            parsing.raise_if(_kurs_razmjene is None)
            _kurs_razmjene = parsing.to_decimal(_kurs_razmjene)

    with parser.get_field(parsing.Fields.INVOICE_NUMBER_OF_INVOICE_ITEMS) as value:
        invoice_number_of_invoice_items = parsing.to_string_or_none(value)
        parsing.raise_if(invoice_number_of_invoice_items is None)
        invoice_number_of_invoice_items = parsing.to_integer(invoice_number_of_invoice_items)

    with parser.get_field(parsing.Fields.INVOICE_NUMBER_OF_TAX_ITEMS) as value:
        invoice_number_of_tax_items = parsing.to_string_or_none(value)
        parsing.raise_if(invoice_number_of_tax_items is None)
        invoice_number_of_tax_items = parsing.to_integer(invoice_number_of_tax_items)

    with parser.get_field(parsing.Fields.INVOICE_HAS_BUYER) as value:
        invoice_has_buyer = parsing.to_string_or_none(value)
        parsing.raise_if(invoice_has_buyer is None)
        invoice_has_buyer = parsing.to_boolean(invoice_has_buyer)

    with parser.get_field(parsing.Fields.INVOICE_NOTE) as value:
        _invoice_note = parsing.to_string_or_none(value)

    out_data = {
        'tip_fakture_id': _invoice_type,
        'datumfakture': _invoice_date_created,
        'ukupna_cijena_osnovna': _invoice_total_base_price,
        'ukupna_cijena_rabatisana': _invoice_total_base_price_with_rebate_only,
        'ukupna_cijena_puna': _invoice_total_base_price_with_tax_only,
        'ukupna_cijena_prodajna': _invoice_total_base_price_with_tax_and_rebate,
        'porez_iznos': _invoice_tax_amount,
        'rabat_iznos_osnovni': _invoice_rebate_amount_before_vat,
        'rabat_iznos_prodajni': _invoice_rebate_amount_after_vat,
        'datumvalute': _invoice_value_date,
        'poreski_period': _invoice_tax_period,
        'is_cash': _invoice_payment_type.is_cash,
        'payment_methods': [{
            'payment_method_type_id': _invoice_payment_type.id
        }],
        'valuta_id': _db_currency.id,
        'kurs_razmjene': _kurs_razmjene,
        'napomena': _invoice_note,
        'stavke': []
    }

    if invoice_has_buyer:
        parser = parsing.Parser(expected_buyer_headers)
        parser.set_headers(tuple(lines.pop(0)), total_lines - len(lines))
        parser.set_values(lines.pop(0), total_lines - len(lines))
        parser.refresh_record()

        with parser.get_field(parsing.Fields.BUYER_IDENTIFICATION_TYPE_ID) as value:
            _tip_identifikacione_oznake_id = parsing.to_string_or_none(value)
            parsing.raise_if(_tip_identifikacione_oznake_id is None)
            _tip_identifikacione_oznake_id = parsing.to_integer(_tip_identifikacione_oznake_id)

        with parser.get_field(parsing.Fields.BUYER_IDENTIFICATION_NUMBER) as value:
            _identifikaciona_oznaka = parsing.to_string_or_none(value)
            parsing.raise_if(_identifikaciona_oznaka is None)

        with parser.get_field(parsing.Fields.BUYER_NAME) as value:
            _naziv = parsing.to_string_or_none(value)
            parsing.raise_if(_naziv is None)

        with parser.get_field(parsing.Fields.BUYER_ADRESS) as value:
            _adresa = parsing.to_string_or_none(value)
            parsing.raise_if(_adresa is None)

        with parser.get_field(parsing.Fields.BUYER_CITY) as value:
            _grad = parsing.to_string_or_none(value)
            parsing.raise_if(_grad is None)

        with parser.get_field(parsing.Fields.BUYER_COUNTRY_CODE) as value:
            _country = helpers.listaj_drzavu_po_iso_kodu(value)
            parsing.raise_if(
                _country is None,
                "Value \"%s\" is not a valid country code." % value)

        _komitent = komitent_opb.po_identifikaciji__listaj(
            _tip_identifikacione_oznake_id, _identifikaciona_oznaka, ovlascenje.firma.pib
        )

        if _komitent is None:
            _komitent = Komitent()
            _komitent.tip_identifikacione_oznake_id = _tip_identifikacione_oznake_id
            _komitent.identifikaciona_oznaka = _identifikaciona_oznaka
            _komitent.pibvlasnikapodatka = ovlascenje.firma.pib
            _komitent.naziv = _naziv
            _komitent.adresa = _naziv
            _komitent.grad = _naziv
            _komitent.drzava = _country.id

            db.session.add(_komitent)
            db.session.commit()

        out_data['komitent_id'] = _komitent.id

        del _tip_identifikacione_oznake_id
        del _identifikaciona_oznaka
        del _komitent
        del _naziv
        del _adresa
        del _grad
        del _country

    parser = parsing.Parser(expected_invoice_item_headers)
    parser.set_headers(tuple(lines.pop(0)), total_lines - len(lines))

    for _ in range(0, invoice_number_of_invoice_items):
        parser.set_values(lines.pop(0), total_lines - len(lines))
        parser.refresh_record()

        with parser.get_field(parsing.Fields.ITEM_DESCRIPTION) as value:
            _naziv = parsing.to_string_or_none(value)
            parsing.raise_if(_naziv is None)

        with parser.get_field(parsing.Fields.ITEM_CODE) as value:
            _sifra = parsing.to_string_or_none(value)
            parsing.raise_if(_sifra is None)

        with parser.get_field(parsing.Fields.ITEM_UNIT_OF_MEASURE) as value:
            _jedinica_mjere_naziv = parsing.to_string_or_none(value)
            parsing.raise_if(_jedinica_mjere_naziv is None)
            _jedinica_mjere = misc_opb.listaj_jedinicu_mjere_po_nazivu(ovlascenje.firma.id, _jedinica_mjere_naziv)
            if _jedinica_mjere is None:
                _jedinica_mjere = JedinicaMjere()
                _jedinica_mjere.naziv = _jedinica_mjere_naziv
                _jedinica_mjere.firma = ovlascenje.firma
                _jedinica_mjere.opis = _jedinica_mjere_naziv
                _jedinica_mjere.ui_default = False
                db.session.add(_jedinica_mjere)
                db.session.commit()

        with parser.get_field(parsing.Fields.ITEM_QUANTITY) as value:
            _kolicina = parsing.to_string_or_none(value)
            parsing.raise_if(_kolicina is None)
            _kolicina = parsing.to_decimal(_kolicina)

        with parser.get_field(parsing.Fields.ITEM_UNIT_BASE_PRICE) as value:
            _jedinicna_cijena_osnovna = parsing.to_string_or_none(value)
            parsing.raise_if(_jedinicna_cijena_osnovna is None)
            _jedinicna_cijena_osnovna = parsing.to_decimal(_jedinicna_cijena_osnovna)

        with parser.get_field(parsing.Fields.ITEM_REBATE_PERCENTAGE) as value:
            _rabat_procenat = parsing.to_string_or_none(value)
            parsing.raise_if(_rabat_procenat is None)
            _rabat_procenat = parsing.to_decimal(_rabat_procenat)

        with parser.get_field(parsing.Fields.ITEM_UNIT_BASE_PRICE_WITH_REBATE_ONLY) as value:
            _jedinicna_cijena_rabatisana = parsing.to_string_or_none(value)
            parsing.raise_if(_jedinicna_cijena_rabatisana is None)
            _jedinicna_cijena_rabatisana = parsing.to_decimal(_jedinicna_cijena_rabatisana)

        with parser.get_field(parsing.Fields.ITEM_UNIT_BASE_PRICE_WITH_TAX_ONLY) as value:
            _jedinicna_cijena_prodajna = parsing.to_string_or_none(value)
            parsing.raise_if(_jedinicna_cijena_prodajna is None)
            _jedinicna_cijena_prodajna = parsing.to_decimal(_jedinicna_cijena_prodajna)

        with parser.get_field(parsing.Fields.ITEM_UNIT_BASE_PRICE_WITH_REBATE_AND_TAX) as value:
            _jedinicna_cijena_puna = parsing.to_string_or_none(value)
            parsing.raise_if(_jedinicna_cijena_puna is None)
            _jedinicna_cijena_puna = parsing.to_decimal(_jedinicna_cijena_puna)

        with parser.get_field(parsing.Fields.ITEM_TOTAL_BASE_PRICE) as value:
            _invoice_total_base_price = parsing.to_string_or_none(value)
            parsing.raise_if(_invoice_total_base_price is None)
            _invoice_total_base_price = parsing.to_decimal(_invoice_total_base_price)

        with parser.get_field(parsing.Fields.ITEM_TOTAL_BASE_PRICE_WITH_REBATE_ONLY) as value:
            _invoice_total_base_price_with_rebate_only = parsing.to_string_or_none(value)
            parsing.raise_if(_invoice_total_base_price_with_rebate_only is None)
            _invoice_total_base_price_with_rebate_only = parsing.to_decimal(_invoice_total_base_price_with_rebate_only)

        with parser.get_field(parsing.Fields.ITEM_TOTAL_BASE_PRICE_WITH_TAX_ONLY) as value:
            _invoice_total_base_price_with_tax_only = parsing.to_string_or_none(value)
            parsing.raise_if(_invoice_total_base_price_with_tax_only is None)
            _invoice_total_base_price_with_tax_only = parsing.to_decimal(_invoice_total_base_price_with_tax_only)

        with parser.get_field(parsing.Fields.ITEM_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX) as value:
            _ukupna_cijena_prodajna = parsing.to_string_or_none(value)
            parsing.raise_if(_ukupna_cijena_prodajna is None)
            _ukupna_cijena_prodajna = parsing.to_decimal(_ukupna_cijena_prodajna)

        with parser.get_field(parsing.Fields.ITEM_TAX_PERCENTAGE) as value:
            _porez_procenat = parsing.to_string_or_none(value)
            if _porez_procenat is not None:
                _porez_procenat = parsing.to_decimal(_porez_procenat)

        with parser.get_field(parsing.Fields.ITEM_VAT_EXEMPTION_REASON_ID) as value:
            _item_vat_exemption_reason_id = parsing.to_string_or_none(value)
            if _item_vat_exemption_reason_id is not None:
                _item_vat_exemption_reason_id = parsing.to_integer(_item_vat_exemption_reason_id)
                _exemption_reason = faktura_opb.get_tax_exemption_reason_by_id(_item_vat_exemption_reason_id)
                parsing.raise_if(
                    _exemption_reason is None,
                    'Value of "item_vat_exemption_reason_id" header on line %s is not a valid value.')
                _porez_procenat = None
                del _exemption_reason

        with parser.get_field(parsing.Fields.ITEM_TOTAL_TAX_AMOUNT) as value:
            _invoice_tax_amount = parsing.to_string_or_none(value)
            parsing.raise_if(_invoice_tax_amount is None)
            _invoice_tax_amount = parsing.to_decimal(_invoice_tax_amount)

        with parser.get_field(parsing.Fields.ITEM_TOTAL_REBATE_AMOUNT_BEFORE_VAT) as value:
            _invoice_rebate_amount_before_vat = parsing.to_string_or_none(value)
            parsing.raise_if(_invoice_rebate_amount_before_vat is None)
            _invoice_rebate_amount_before_vat = parsing.to_decimal(_invoice_rebate_amount_before_vat)

        with parser.get_field(parsing.Fields.ITEM_TOTAL_REBATE_AMOUNT_AFTER_VAT) as value:
            _invoice_rebate_amount_after_vat = parsing.to_string_or_none(value)
            parsing.raise_if(_invoice_rebate_amount_after_vat is None)
            _invoice_rebate_amount_after_vat = parsing.to_decimal(_invoice_rebate_amount_after_vat)

        out_data['stavke'].append({
            'izvor_kalkulacije': 2,
            'naziv': _naziv,
            'sifra': _sifra,
            'jedinica_mjere_id': _jedinica_mjere.id,
            'kolicina': _kolicina,
            'jedinicna_cijena_osnovna': _jedinicna_cijena_osnovna,
            'rabat_procenat': _rabat_procenat,
            'jedinicna_cijena_puna': _jedinicna_cijena_puna,
            'jedinicna_cijena_rabatisana': _jedinicna_cijena_rabatisana,
            'jedinicna_cijena_prodajna': _jedinicna_cijena_prodajna,
            'ukupna_cijena_osnovna': _invoice_total_base_price,
            'ukupna_cijena_rabatisana': _invoice_total_base_price_with_rebate_only,
            'ukupna_cijena_puna': _invoice_total_base_price_with_tax_only,
            'ukupna_cijena_prodajna': _ukupna_cijena_prodajna,
            'porez_procenat': _porez_procenat,
            'tax_exemption_reason_id': _item_vat_exemption_reason_id,
            'tax_exemption_amount': 0 if _item_vat_exemption_reason_id is None else _ukupna_cijena_prodajna,
            'porez_iznos': _invoice_tax_amount,
            'rabat_iznos_osnovni': _invoice_rebate_amount_before_vat,
            'rabat_iznos_prodajni': _invoice_rebate_amount_after_vat
        })

        del _naziv
        del _sifra
        del _jedinica_mjere_naziv
        del _jedinica_mjere
        del _kolicina
        del _jedinicna_cijena_osnovna
        del _rabat_procenat
        del _jedinicna_cijena_rabatisana
        del _jedinicna_cijena_prodajna
        del _jedinicna_cijena_puna
        del _invoice_total_base_price
        del _invoice_total_base_price_with_rebate_only
        del _invoice_total_base_price_with_tax_only
        del _ukupna_cijena_prodajna
        del _porez_procenat
        del _item_vat_exemption_reason_id
        del _invoice_tax_amount
        del _invoice_rebate_amount_before_vat
        del _invoice_rebate_amount_after_vat

    parser = parsing.Parser(expected_sametax_item_headers)
    parser.set_headers(tuple(lines.pop(0)), total_lines - len(lines))

    for _ in range(0, invoice_number_of_tax_items):
        parser.set_values(lines.pop(0), total_lines - len(lines))
        parser.refresh_record()

        with parser.get_field(parsing.Fields.TAX_GROUP_NUMBER_OF_MATCHED_INVOICE_ITEMS) as value:
            _broj_stavki = parsing.to_decimal(value)

        with parser.get_field(parsing.Fields.TAX_GROUP_BASE_PRICE) as value:
            _invoice_total_base_price = parsing.to_decimal(value)

        with parser.get_field(parsing.Fields.TAX_GROUP_BASE_PRICE_WITH_REBATE) as value:
            _invoice_total_base_price_with_rebate_only = parsing.to_decimal(value)

        with parser.get_field(parsing.Fields.TAX_GROUP_BASE_PRICE_WITH_TAX) as value:
            _invoice_total_base_price_with_tax_only = parsing.to_decimal(value)

        with parser.get_field(parsing.Fields.TAX_GROUP_BASE_PRICE_WITH_REBATE_AND_TAX) as value:
            _ukupna_cijena_prodajna = parsing.to_decimal(value)

        with parser.get_field(parsing.Fields.TAX_GROUP_TAX_PERCENTAGE) as value:
            _porez_procenat = parsing.to_decimal(value)

        # TODO Add tax exemption reason

        with parser.get_field(parsing.Fields.TAX_GROUP_TAX_AMOUNT) as value:
            _invoice_tax_amount = parsing.to_decimal(value)

        with parser.get_field(parsing.Fields.TAX_GROUP_REBATE_AMOUNT_BEFORE_VAT) as value:
            _invoice_rebate_amount_before_vat = parsing.to_decimal(value)

        with parser.get_field(parsing.Fields.TAX_GROUP_REBATE_AMOUNT_AFTER_VAT) as value:
            _invoice_rebate_amount_after_vat = parsing.to_decimal(value)

        del _broj_stavki
        del _invoice_total_base_price
        del _invoice_total_base_price_with_rebate_only
        del _invoice_total_base_price_with_tax_only
        del _ukupna_cijena_prodajna
        del _porez_procenat
        del _invoice_tax_amount
        del _invoice_rebate_amount_before_vat
        del _invoice_rebate_amount_after_vat

    # ------------------------------------------------------------------------------------------------------------------
    # TODO Refactor
    out_data['tax_exemption_amount'] = Decimal(0)
    for stavka in out_data['stavke']:
        if stavka['tax_exemption_reason_id'] is not None:
            out_data['tax_exemption_amount'] += Decimal(stavka['tax_exemption_amount'])
    # ------------------------------------------------------------------------------------------------------------------

    return out_data, ovlascenje.firma, operater, naplatni_uredjaj, faktura_za_korekciju


def create_output_from_invoice(input_filepath, invoice, faultcode, faultstring):
    with open(input_filepath) as input_file:
        reader = csv.reader(input_file, delimiter=',')
        lines = []
        for row in reader:
            lines.append(row)

    lines[0].append('invoice_efi_number')
    lines[1].append("" if invoice is None else invoice.efi_broj_fakture)

    lines[0].append('invoice_efi_verify_url')
    lines[1].append("" if invoice is None else invoice.efi_verify_url)

    lines[0].append('invoice_iic_number')
    lines[1].append("" if invoice is None else invoice.ikof)

    lines[0].append('invoice_fic_number')
    lines[1].append("" if invoice is None else invoice.jikr)

    lines[0].append('invoice_fault_code')
    lines[1].append(faultcode)

    lines[0].append('invoice_fault_string')
    lines[1].append(faultstring)

    return lines


def save_output(filepath, lines):
    with open(filepath, 'w') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        writer.writerows(lines)
