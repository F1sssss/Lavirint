import decimal
from datetime import datetime
from io import BytesIO

import pytz
from _decimal import Decimal
from lxml import etree

from backend import efi_xml
from backend import i18n
from backend import patterns
from backend.db import db
from backend.logging import logger
from backend.models import Faktura
from backend.models import JedinicaMjere
from backend.models import Komitent
from backend.opb import faktura_opb, operater_opb
from backend.opb import firma_opb
from backend.opb import helpers
from backend.opb import komitent_opb
from backend.opb import misc_opb
from backend.opb import soap_opb
from backend.podesavanja import podesavanja

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
SOAP_NS_ESCAPED = '{%s}' % SOAP_NS

ELAVIRINT_NS = podesavanja.SOAP_API_ELAVIRINT_NAMESPACE
ELAVIRINT_NS_ESCAPED = '{%s}' % ELAVIRINT_NS


class XmlParseError(Exception):

    def __init__(self, data):
        self.data = data


def parse(element, data_type, pattern=None):
    value = element.text

    if value is None or len(value) == 0:
        raise XmlParseError({
            'xpath': get_xpath(element),
            'description': 'Missing element value.'
        })

    if pattern is not None and pattern.search(value) is None:
        raise XmlParseError({
            'xpath': get_xpath(element),
            'description': 'Element value is not formatted correctly.'
        })

    if data_type == str:
        return value
    elif data_type == int:
        try:
            return int(value)
        except TypeError:
            raise XmlParseError({
                'xpath': get_xpath(element),
                'description': 'Element value is not formatted correctly.'
            })
        except ValueError:
            raise XmlParseError({
                'xpath': get_xpath(element),
                'description': 'Element value is not formatted correctly.'
            })
    elif data_type == decimal.Decimal:
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation:
            raise XmlParseError({
                'xpath': get_xpath(element),
                'description': 'Element value is not formatted correctly.'
            })
    elif data_type == datetime:
        try:
            return datetime \
                .fromisoformat(value.replace('Z', '+00:00')) \
                .astimezone(pytz.timezone('Europe/Podgorica')) \
                .isoformat()
        except ValueError:
            raise XmlParseError({
                'xpath': get_xpath(element),
                'description': 'Element value is not formatted correctly.'
            })
    elif data_type == bool:
        if value in ['0', 'false']:
            return False
        elif value in ['1', 'true']:
            return True
        else:
            raise TypeError({
                'xpath': get_xpath(element),
                'description': 'Element value is not formatted correctly.'
            })
    else:
        raise ValueError('Invalid data type.')


def get_xpath(element):
    tree = element.getroottree()
    element_path = tree.getelementpath(element)

    if element_path == '.':
        return '/' + tree.getroot().tag

    return '/' + tree.getroot().tag + '/' + tree.getelementpath(element)


def is_xpath(element, expected_xpath):
    return get_xpath(element) == expected_xpath


def raise_if_not_xpath(element, expected_xpath):
    xpath = get_xpath(element)

    if xpath == expected_xpath:
        return True

    raise XmlParseError({
        'xpath': xpath,
        'expected_element': expected_xpath,
        'description': 'Missing required element.'
    })


def soap_xml_to_invoice_dict(soap_user, xml):
    if isinstance(xml, BytesIO):
        xml = xml.read()

    try:
        root = etree.fromstring(xml)
    except Exception as exception:
        logger.exception("Error while parsing SOAP XML", extra={
            'xml': xml
        })

    raise_if_not_xpath(root, f'/{SOAP_NS_ESCAPED}Envelope')

    envelope_children_iterator = root.iterchildren()

    expected_xpath = f'/{SOAP_NS_ESCAPED}Envelope/{SOAP_NS_ESCAPED}Body'
    try:
        body_element = envelope_children_iterator.__next__()
        raise_if_not_xpath(body_element, expected_xpath)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element.'
        })

    body_children_iterator = body_element.iterchildren()

    invoice_xpath = f'/{SOAP_NS_ESCAPED}Envelope/{SOAP_NS_ESCAPED}Body/{ELAVIRINT_NS_ESCAPED}Invoice'
    try:

        invoice_element = body_children_iterator.__next__()
        raise_if_not_xpath(invoice_element, invoice_xpath)
    except StopIteration:
        raise XmlParseError({
            'xpath': invoice_xpath,
            'description': 'Missing required element'
        })

    invoice_iterator = invoice_element.iterchildren()

    invoice_seller_identification_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}SellerIdentificationNumber'
    try:
        element = invoice_iterator.__next__()
    except StopIteration:
        raise XmlParseError({
            'xpath': invoice_seller_identification_xpath,
            'description': 'Missing required element'
        })

    raise_if_not_xpath(element, invoice_seller_identification_xpath)
    seller_identification_number = parse(element, data_type=str)
    company = firma_opb.listaj_po_pibu(seller_identification_number)
    if company is None:
        raise XmlParseError({
            'xpath': invoice_seller_identification_xpath,
            'description': 'Invalid value.'
        })

    permission = soap_opb.get_soap_permission_by_user_id_and_company_id(soap_user.id, company.id)
    if permission is None:
        raise XmlParseError({
            'xpath': invoice_seller_identification_xpath,
            'description': 'Not authorized to create invoice on behalf of seller with specified identification number.'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}Type'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        tip_fakture = parse(element, data_type=int, pattern=patterns.identification_type_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    if tip_fakture == Faktura.TYPE_REGULAR:
        data, company, operator = read_regular_invoice_from_xml(invoice_iterator, company)
        return tip_fakture, data, company, operator, None, datetime.fromisoformat(data['datumfakture'])
    elif tip_fakture == Faktura.TYPE_CANCELLATION:
        return read_total_corrective_invoice_from_xml(invoice_iterator, company)
    elif tip_fakture == Faktura.TYPE_CORRECTIVE:
        raise NotImplementedError()
    elif tip_fakture == Faktura.TYPE_ADVANCE:
        data, company, operator = read_regular_invoice_from_xml(invoice_iterator, company)
        return tip_fakture, data, company, operator, None, datetime.fromisoformat(data['datumfakture'])
    else:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': f'Invalid value. Available values are: {Faktura.TYPE_REGULAR}, {Faktura.TYPE_CANCELLATION}.'
        })


def read_total_corrective_invoice_from_xml(invoice_iterator, company):
    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}DateCreated'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        datumfakture = parse(element, data_type=datetime, pattern=patterns.utc_stype)
        datumfakture = datetime.fromisoformat(datumfakture)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}OperatorEfiCode'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        operator_efi_code = parse(element, data_type=str, pattern=patterns.registration_code_stype)
        operator = operater_opb.get_customer_user_by_efi_code(company.id, operator_efi_code)
        if operator is None:
            raise XmlParseError({
                'xpath': expected_xpath,
                'description': 'Invalid value.'
            })
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}CorrectedInvoiceIICReference'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        corrected_invoice_iic = parse(element, data_type=str, pattern=patterns.hex_32_stype)

        korigovana_faktura = faktura_opb.get_invoice_by_company_id_and_iic(company.id, corrected_invoice_iic)
        if korigovana_faktura is None:
            raise XmlParseError({
                'xpath': expected_xpath,
                'description': 'Corrected invoice IIC reference does not exist.'
            })

        if korigovana_faktura.firma.pib != company.pib:
            raise XmlParseError({
                'xpath': expected_xpath,
                'description': 'Corrected invoice IIC reference does not exist.'
            })
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    return 2, {}, company, operator, korigovana_faktura, datumfakture


def read_partial_corrective_invoice_from_xml(invoice_iterator, company):
    pass


def read_regular_invoice_from_xml(invoice_iterator, company):
    podaci = {
        'stavke': [],
        'grupe_poreza': []
    }

    invoice_xpath = f'/{SOAP_NS_ESCAPED}Envelope/{SOAP_NS_ESCAPED}Body/{ELAVIRINT_NS_ESCAPED}Invoice'

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}DateCreated'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        podaci['datumfakture'] = parse(element, data_type=datetime, pattern=patterns.utc_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}ValueDate'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        podaci['datumvalute'] = parse(element, data_type=datetime, pattern=patterns.utc_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}TaxPeriod'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        poreski_period = parse(element, data_type=str, pattern=patterns.tax_period_stype)
        poreski_period_split = poreski_period.split('/')
        month = int(poreski_period_split[0])
        year = int(poreski_period_split[1])
        podaci['poreski_period'] = datetime.now()
        podaci['poreski_period'] = podaci['poreski_period'].replace(day=1, hour=0, minute=0, second=0, microsecond=0,
                                                                    month=month, year=year)
        podaci['poreski_period'] = podaci['poreski_period'].isoformat()
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}PaymentTypeId'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        vrsta_placanja_id = parse(element, data_type=int)
        payment_method_type = faktura_opb.get_payment_method_type_by_id(vrsta_placanja_id)
        if not payment_method_type:
            raise XmlParseError({
                'xpath': expected_xpath,
                'description': 'Invalid value.'
            })
        podaci['is_cash'] = payment_method_type.is_cash
        podaci['payment_methods'] = [{
            'payment_method_type_id': vrsta_placanja_id
        }]
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}OperatorEfiCode'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        operator_efi_code = parse(element, data_type=str, pattern=patterns.registration_code_stype)
        operator = operater_opb.get_customer_user_by_efi_code(company.id, operator_efi_code)
        if operator is None:
            raise XmlParseError({
                'xpath': expected_xpath,
                'description': 'Invalid value.'
            })
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}TotalBasePrice'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        podaci['ukupna_cijena_osnovna'] = parse(element, data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}TotalBasePriceWithRebateOnly'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        podaci['ukupna_cijena_rabatisana'] = parse(element, data_type=decimal.Decimal,
                                                   pattern=patterns.decimal_neg_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}TotalBasePriceWithTaxOnly'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        podaci['ukupna_cijena_puna'] = parse(element, data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}TotalBasePriceWithRebateAndTax'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        podaci['ukupna_cijena_prodajna'] = parse(element, data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}TaxAmount'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        podaci['porez_iznos'] = parse(element, data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}RebateAmountBeforeVat'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        podaci['rabat_iznos_osnovni'] = parse(element, data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}RebateAmountAfterVat'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        podaci['rabat_iznos_prodajni'] = parse(element, data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}CorrectionInvoiceIICReference'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        # TODO
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    expected_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}CurrencyIsoCode'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, expected_xpath)
        currency_iso_code = parse(element, data_type=str)
        currency = misc_opb.listaj_valutu_po_iso_kodu(currency_iso_code)
        if currency is None:
            raise XmlParseError({
                'xpath': expected_xpath,
                'description': 'Invalid value.'
            })
        podaci['valuta_id'] = currency.id
    except StopIteration:
        raise XmlParseError({
            'xpath': expected_xpath,
            'description': 'Missing required element'
        })

    invoice_currecy_exchange_rate = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}CurrencyExchangeRate'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, invoice_currecy_exchange_rate)
        podaci['kurs_razmjene'] = parse(element, data_type=decimal.Decimal)
    except StopIteration:
        raise XmlParseError({
            'xpath': invoice_currecy_exchange_rate,
            'description': 'Missing required element'
        })

    invoice_note_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}Note'

    invoice_items_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}Items'

    try:
        element = invoice_iterator.__next__()
    except StopIteration:
        raise XmlParseError({
            'xpath': invoice_items_xpath,
            'description': 'Unexpected end of element'
        })

    if is_xpath(element, invoice_note_xpath):
        podaci['napomena'] = parse(element, data_type=str)

        try:
            element = invoice_iterator.__next__()
        except StopIteration:
            raise XmlParseError({
                'xpath': invoice_items_xpath,
                'description': 'Unexpected end of element'
            })
        pass

    invoice_buyer_xpath = \
        f'/{SOAP_NS_ESCAPED}Envelope' \
        f'/{SOAP_NS_ESCAPED}Body' \
        f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
        f'/{ELAVIRINT_NS_ESCAPED}Buyer'
    if is_xpath(element, invoice_buyer_xpath):
        buyer_children_iterator = element.iterchildren()

        identification_type_id_xpath = f'{invoice_buyer_xpath}/{ELAVIRINT_NS_ESCAPED}IdentificationTypeId'
        try:
            buyer_identification_type_element = buyer_children_iterator.__next__()
            raise_if_not_xpath(buyer_identification_type_element, identification_type_id_xpath)
            buyer_identification_type_id = parse(buyer_identification_type_element, data_type=int)
        except StopIteration:
            raise XmlParseError({
                'xpath': identification_type_id_xpath,
                'description': 'Unexpected end of element'
            })
        pass

        identification_number_xpath = f'{invoice_buyer_xpath}/{ELAVIRINT_NS_ESCAPED}IdentificationNumber'
        try:
            buyer_identification_number_element = buyer_children_iterator.__next__()
            raise_if_not_xpath(buyer_identification_number_element, identification_number_xpath)
            buyer_identification_number = parse(buyer_identification_number_element, data_type=str)
        except StopIteration:
            raise XmlParseError({
                'xpath': identification_number_xpath,
                'description': 'Unexpected end of element'
            })

        name_xpath = f'{invoice_buyer_xpath}/{ELAVIRINT_NS_ESCAPED}Name'
        try:
            buyer_name_element = buyer_children_iterator.__next__()
            raise_if_not_xpath(buyer_name_element, name_xpath)
            buyer_name = parse(buyer_name_element, data_type=str)
        except StopIteration:
            raise XmlParseError({
                'xpath': name_xpath,
                'description': 'Unexpected end of element'
            })

        adress_xpath = f'{invoice_buyer_xpath}/{ELAVIRINT_NS_ESCAPED}Adress'
        try:
            buyer_adress_element = buyer_children_iterator.__next__()
            raise_if_not_xpath(buyer_adress_element, adress_xpath)
            buyer_adress = parse(buyer_adress_element, data_type=str)
        except StopIteration:
            raise XmlParseError({
                'xpath': adress_xpath,
                'description': 'Unexpected end of element'
            })

        city_xpath = f'{invoice_buyer_xpath}/{ELAVIRINT_NS_ESCAPED}City'
        try:
            buyer_city_element = buyer_children_iterator.__next__()
            raise_if_not_xpath(buyer_city_element, city_xpath)
            buyer_city = parse(buyer_city_element, data_type=str)
        except StopIteration:
            raise XmlParseError({
                'xpath': city_xpath,
                'description': 'Unexpected end of element'
            })

        country_code_xpath = f'{invoice_buyer_xpath}/{ELAVIRINT_NS_ESCAPED}CountryCode'
        try:
            buyer_country_code_element = buyer_children_iterator.__next__()
            raise_if_not_xpath(buyer_country_code_element, country_code_xpath)
            buyer_country_code = parse(buyer_country_code_element, data_type=str)
            buyer_country = helpers.listaj_drzavu_po_iso_kodu(buyer_country_code)
            if buyer_country is None:
                raise XmlParseError({
                    'xpath': country_code_xpath,
                    'description': 'Invalid value.'
                })
        except StopIteration:
            raise XmlParseError({
                'xpath': country_code_xpath,
                'description': 'Unexpected end of element'
            })

        if company.pib == '02908301':
            if buyer_country_code == 'MNE':
                if len(buyer_identification_number) == 8:
                    buyer_identification_type_id = 2
                elif len(buyer_identification_number) == 13:
                    buyer_identification_type_id = 1
                else:
                    raise XmlParseError({
                        'xpath': identification_number_xpath,
                        'description': 'Invalid value.'
                    })
            else:
                buyer_identification_type_id = 6
        else:
            if buyer_identification_type_id == 1:
                if len(buyer_identification_number) != 13:
                    raise XmlParseError({
                        'xpath': identification_number_xpath,
                        'description': 'Invalid value.'
                    })
            elif buyer_identification_type_id == 2:
                if len(buyer_identification_number) != 8:
                    raise XmlParseError({
                        'xpath': identification_number_xpath,
                        'description': 'Invalid value.'
                    })
            elif buyer_identification_type_id == 6:
                # No check is made for foreign buyers
                pass
            else:
                raise XmlParseError({
                    'xpath': identification_type_id_xpath,
                    'description': 'Invalid value.'
                })

        buyer = komitent_opb.po_identifikaciji__listaj(
            buyer_identification_type_id, buyer_identification_number, company.pib)
        if buyer is None:
            buyer = Komitent()
            buyer.tip_identifikacione_oznake_id = buyer_identification_type_id
            buyer.identifikaciona_oznaka = buyer_identification_number

            buyer.pibvlasnikapodatka = company.pib
            buyer.naziv = buyer_name
            buyer.adresa = buyer_adress
            buyer.grad = buyer_city
            buyer.drzava = buyer_country.id

            db.session.add(buyer)
            db.session.commit()

        podaci['komitent_id'] = buyer.id

        try:
            element = invoice_iterator.__next__()
        except StopIteration:
            raise XmlParseError({
                'xpath': invoice_items_xpath,
                'description': 'Unexpected end of element'
            })
        pass

    raise_if_not_xpath(element, invoice_items_xpath)

    items_children = element.getchildren()
    if len(items_children) == 0:
        raise XmlParseError({
            'description': 'Missing invoice item elements'
        })
    else:
        for index, element in enumerate(items_children):
            if len(items_children) == 1:
                item_xpath = \
                    f'/{SOAP_NS_ESCAPED}Envelope' \
                    f'/{SOAP_NS_ESCAPED}Body' \
                    f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
                    f'/{ELAVIRINT_NS_ESCAPED}Items' \
                    f'/{ELAVIRINT_NS_ESCAPED}Item'
            else:
                item_xpath = \
                    f'/{SOAP_NS_ESCAPED}Envelope' \
                    f'/{SOAP_NS_ESCAPED}Body' \
                    f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
                    f'/{ELAVIRINT_NS_ESCAPED}Items' \
                    f'/{ELAVIRINT_NS_ESCAPED}Item[%s]' % (index + 1)

            invoice_item = {
                'izvor_kalkulacije': 2
            }
            podaci['stavke'].append(invoice_item)

            raise_if_not_xpath(items_children[index], item_xpath)

            item_iterator = items_children[index].iterchildren()

            item_code_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}Code'

            item_description_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}Description'

            item_unit_base_price_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}UnitBasePrice'

            item_rebate_percentage_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}RebatePercentage'

            item_tax_percentage_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TaxPercentage'

            item_unit_base_price_with_rebate_only_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}UnitBasePriceWithRebateOnly'

            item_unit_base_price_with_tax_only_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}UnitBasePriceWithTaxOnly'

            item_unit_base_price_with_rebate_and_tax_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}UnitBasePriceWithRebateAndTax'

            item_unit_of_measure_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}UnitOfMeasure'

            item_quantity_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}Quantity'

            item_total_base_price_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TotalBasePrice'

            item_total_base_price_with_rebate_only_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TotalBasePriceWithRebateOnly'

            item_total_base_price_with_tax_only_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TotalBasePriceWithTaxOnly'

            item_total_base_price_with_rebate_and_tax_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TotalBasePriceWithRebateAndTax'

            item_total_tax_amount_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TotalTaxAmount'

            item_total_rebate_amount_before_vat_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TotalRebateAmountBeforeVat'

            item_total_rebate_amount_after_vat_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TotalRebateAmountAfterVat'

            item_vat_exemption_reason_id_xpath = \
                f'{item_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}VatExemptionReasonId'

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_code_xpath)
                invoice_item['sifra'] = parse(element, data_type=int)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_code_xpath
                    ],
                    'xpath': item_code_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_description_xpath)
                invoice_item['naziv'] = parse(element, data_type=str)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_description_xpath
                    ],
                    'xpath': item_description_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_unit_base_price_xpath)
                invoice_item['jedinicna_cijena_osnovna'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_unit_base_price_xpath
                    ],
                    'xpath': item_unit_base_price_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_rebate_percentage_xpath)
                invoice_item['rabat_procenat'] = parse(element, data_type=decimal.Decimal,
                                                       pattern=patterns.decimal_4_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_rebate_percentage_xpath
                    ],
                    'xpath': item_rebate_percentage_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_tax_percentage_xpath)
                invoice_item['porez_procenat'] = parse(element, data_type=decimal.Decimal,
                                                       pattern=patterns.decimal_4_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_tax_percentage_xpath
                    ],
                    'xpath': item_tax_percentage_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_unit_base_price_with_rebate_only_xpath)
                invoice_item['jedinicna_cijena_rabatisana'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_unit_base_price_with_rebate_only_xpath
                    ],
                    'xpath': item_unit_base_price_with_rebate_only_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_unit_base_price_with_tax_only_xpath)
                invoice_item['jedinicna_cijena_puna'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_unit_base_price_with_tax_only_xpath
                    ],
                    'xpath': item_unit_base_price_with_tax_only_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_unit_base_price_with_rebate_and_tax_xpath)
                invoice_item['jedinicna_cijena_prodajna'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_unit_base_price_with_rebate_and_tax_xpath
                    ],
                    'xpath': item_unit_base_price_with_rebate_and_tax_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_unit_of_measure_xpath)
                unit_of_measure_name = parse(element, data_type=str)
                unit_of_measure = misc_opb.listaj_jedinicu_mjere_po_nazivu(company.id, unit_of_measure_name)
                if unit_of_measure is None:
                    unit_of_measure = JedinicaMjere()
                    unit_of_measure.naziv = unit_of_measure_name
                    unit_of_measure.firma = company
                    unit_of_measure.opis = unit_of_measure_name
                    unit_of_measure.ui_default = False
                    db.session.add(unit_of_measure)
                    db.session.commit()
                    db.session.refresh(unit_of_measure)
                invoice_item['jedinica_mjere_id'] = unit_of_measure.id
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_unit_of_measure_xpath
                    ],
                    'xpath': item_unit_of_measure_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_quantity_xpath)
                invoice_item['kolicina'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.double_neg_for_quantity_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_quantity_xpath
                    ],
                    'xpath': item_quantity_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_total_base_price_xpath)
                invoice_item['ukupna_cijena_osnovna'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_total_base_price_xpath
                    ],
                    'xpath': item_total_base_price_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_total_base_price_with_rebate_only_xpath)
                invoice_item['ukupna_cijena_rabatisana'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_total_base_price_with_rebate_only_xpath
                    ],
                    'xpath': item_total_base_price_with_rebate_only_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_total_base_price_with_tax_only_xpath)
                invoice_item['ukupna_cijena_puna'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_total_base_price_with_tax_only_xpath
                    ],
                    'xpath': item_total_base_price_with_tax_only_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_total_base_price_with_rebate_and_tax_xpath)
                invoice_item['ukupna_cijena_prodajna'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_total_base_price_with_rebate_and_tax_xpath
                    ],
                    'xpath': item_total_base_price_with_rebate_and_tax_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_total_tax_amount_xpath)
                invoice_item['porez_iznos'] = parse(element, data_type=decimal.Decimal,
                                                    pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_total_tax_amount_xpath
                    ],
                    'xpath': item_total_tax_amount_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_total_rebate_amount_before_vat_xpath)
                invoice_item['rabat_iznos_osnovni'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_total_rebate_amount_before_vat_xpath
                    ],
                    'xpath': item_total_rebate_amount_before_vat_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_total_rebate_amount_after_vat_xpath)
                invoice_item['rabat_iznos_prodajni'] = parse(
                    element,
                    data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        item_total_rebate_amount_after_vat_xpath
                    ],
                    'xpath': item_total_rebate_amount_after_vat_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = item_iterator.__next__()
                raise_if_not_xpath(element, item_vat_exemption_reason_id_xpath)
                tax_exemption_reason_id = parse(element, data_type=int)

                if tax_exemption_reason_id is not None:
                    tax_exemption_reason = faktura_opb.get_tax_exemption_reason_by_id(tax_exemption_reason_id)
                    if tax_exemption_reason is None:
                        raise XmlParseError({
                            'xpath': item_vat_exemption_reason_id_xpath,
                            'description': 'Invalid value.'
                        })
                    invoice_item['tax_exemption_reason_id'] = tax_exemption_reason_id
                    invoice_item['tax_exemption_amount'] = invoice_item['ukupna_cijena_prodajna']
                else:
                    invoice_item['tax_exemption_reason_id'] = None
                    invoice_item['tax_exemption_amount'] = 0

                # TODO raise error if both tax_rate and tax_exemption_reason_id is None

            except StopIteration:
                invoice_item['tax_exemption_reason_id'] = None
                invoice_item['tax_exemption_amount'] = 0

    invoice_tax_groups_xpath = f'{invoice_xpath}/{ELAVIRINT_NS_ESCAPED}TaxGroups'
    try:
        element = invoice_iterator.__next__()
        raise_if_not_xpath(element, invoice_tax_groups_xpath)
    except StopIteration:
        if company.je_poreski_obaveznik:
            raise XmlParseError({
                'expected_xpath': [
                    invoice_tax_groups_xpath
                ],
                'xpath': invoice_tax_groups_xpath,
                'description': 'Unexpected end of element'
            })

    if company.je_poreski_obaveznik:
        tax_groups_children = element.getchildren()
        for index, tax_group_element in enumerate(tax_groups_children):
            if len(tax_groups_children) == 1:
                tax_group_xpath = \
                    f'/{SOAP_NS_ESCAPED}Envelope' \
                    f'/{SOAP_NS_ESCAPED}Body' \
                    f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
                    f'/{ELAVIRINT_NS_ESCAPED}TaxGroups' \
                    f'/{ELAVIRINT_NS_ESCAPED}TaxGroup'
            else:
                tax_group_xpath = \
                    f'/{SOAP_NS_ESCAPED}Envelope' \
                    f'/{SOAP_NS_ESCAPED}Body' \
                    f'/{ELAVIRINT_NS_ESCAPED}Invoice' \
                    f'/{ELAVIRINT_NS_ESCAPED}TaxGroups' \
                    f'/{ELAVIRINT_NS_ESCAPED}TaxGroup[%s]' % (index + 1)

            tax_group = {}
            tax_group['tax_exemption_reason_id'] = None
            podaci['grupe_poreza'].append(tax_group)

            raise_if_not_xpath(tax_group_element, tax_group_xpath)

            tax_group_children_iterator = tax_group_element.iterchildren()

            tax_group_number_of_matched_invoice_items_xpath = \
                f'{tax_group_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}NumberOfMatchedInvoiceItems'

            tax_group_base_price_xpath = \
                f'{tax_group_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}BasePrice'

            tax_group_base_price_with_rebate_only_xpath = \
                f'{tax_group_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}BasePriceWithRebateOnly'

            tax_group_base_price_with_tax_only_xpath = \
                f'{tax_group_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}BasePriceWithTaxOnly'

            tax_group_base_price_with_rebate_and_tax_xpath = \
                f'{tax_group_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}BasePriceWithRebateAndTax'

            tax_group_tax_percentage_xpath = \
                f'{tax_group_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TaxPercentage'

            tax_group_tax_amount_xpath = \
                f'{tax_group_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}TaxAmount'

            tax_group_rebate_amount_before_vat_xpath = \
                f'{tax_group_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}RebateAmountBeforeVat'

            tax_group_rebate_amount_after_vat_xpath = \
                f'{tax_group_xpath}' \
                f'/{ELAVIRINT_NS_ESCAPED}RebateAmountAfterVat'

            try:
                element = tax_group_children_iterator.__next__()
                raise_if_not_xpath(element, tax_group_number_of_matched_invoice_items_xpath)
                tax_group['broj_stavki'] = parse(element, data_type=int)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        tax_group_number_of_matched_invoice_items_xpath
                    ],
                    'xpath': tax_group_number_of_matched_invoice_items_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = tax_group_children_iterator.__next__()
                raise_if_not_xpath(element, tax_group_base_price_xpath)
                tax_group['ukupna_cijena_osnovna'] = parse(element, data_type=decimal.Decimal,
                                                           pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        tax_group_base_price_xpath
                    ],
                    'xpath': tax_group_base_price_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = tax_group_children_iterator.__next__()
                raise_if_not_xpath(element, tax_group_base_price_with_rebate_only_xpath)
                tax_group['ukupna_cijena_rabatisana'] = parse(element, data_type=decimal.Decimal,
                                                              pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        tax_group_base_price_with_rebate_only_xpath
                    ],
                    'xpath': tax_group_base_price_with_rebate_only_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = tax_group_children_iterator.__next__()
                raise_if_not_xpath(element, tax_group_base_price_with_tax_only_xpath)
                tax_group['ukupna_cijena_puna'] = parse(element, data_type=decimal.Decimal,
                                                        pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        tax_group_base_price_with_tax_only_xpath
                    ],
                    'xpath': tax_group_base_price_with_tax_only_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = tax_group_children_iterator.__next__()
                raise_if_not_xpath(element, tax_group_base_price_with_rebate_and_tax_xpath)
                tax_group['ukupna_cijena_prodajna'] = parse(element, data_type=decimal.Decimal,
                                                            pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        tax_group_base_price_with_rebate_and_tax_xpath
                    ],
                    'xpath': tax_group_base_price_with_rebate_and_tax_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = tax_group_children_iterator.__next__()
                raise_if_not_xpath(element, tax_group_tax_percentage_xpath)
                tax_group['porez_procenat'] = parse(element, data_type=decimal.Decimal, pattern=patterns.decimal_4_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        tax_group_tax_percentage_xpath
                    ],
                    'xpath': tax_group_tax_percentage_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = tax_group_children_iterator.__next__()
                raise_if_not_xpath(element, tax_group_tax_amount_xpath)
                tax_group['porez_iznos'] = parse(element, data_type=decimal.Decimal, pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        tax_group_tax_amount_xpath
                    ],
                    'xpath': tax_group_tax_amount_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = tax_group_children_iterator.__next__()
                raise_if_not_xpath(element, tax_group_rebate_amount_before_vat_xpath)
                tax_group['rabat_iznos_osnovni'] = parse(element, data_type=decimal.Decimal,
                                                         pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        tax_group_rebate_amount_before_vat_xpath
                    ],
                    'xpath': tax_group_rebate_amount_before_vat_xpath,
                    'description': 'Unexpected end of element'
                })

            try:
                element = tax_group_children_iterator.__next__()
                raise_if_not_xpath(element, tax_group_rebate_amount_after_vat_xpath)
                tax_group['rabat_iznos_prodajni'] = parse(element, data_type=decimal.Decimal,
                                                          pattern=patterns.decimal_neg_stype)
            except StopIteration:
                raise XmlParseError({
                    'expected_elements': [
                        tax_group_rebate_amount_after_vat_xpath
                    ],
                    'xpath': tax_group_rebate_amount_after_vat_xpath,
                    'description': 'Unexpected end of element'
                })

    # ------------------------------------------------------------------------------------------------------------------
    # TODO Refactor
    podaci['tax_exemption_amount'] = Decimal(0)
    for stavka in podaci['stavke']:
        if stavka['tax_exemption_reason_id'] is not None:
            podaci['tax_exemption_amount'] += Decimal(stavka['tax_exemption_amount'])
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # TODO Refactor
    _exemption_groups = {}
    for stavka in podaci['stavke']:
        exemption_reason = stavka['tax_exemption_reason_id']
        if exemption_reason is None:
            continue

        if exemption_reason not in _exemption_groups:
            _exemption_groups[exemption_reason] = {
                'broj_stavki': Decimal(0),
                'ukupna_cijena_osnovna': Decimal(0),
                'ukupna_cijena_rabatisana': Decimal(0),
                'ukupna_cijena_puna': Decimal(0),
                'ukupna_cijena_prodajna': Decimal(0),
                'porez_procenat': None,
                'porez_iznos': Decimal(0),
                'rabat_iznos_osnovni': Decimal(0),
                'rabat_iznos_prodajni': Decimal(0),
                'credit_note_turnover_used': Decimal(0),
                'credit_note_turnover_remaining': Decimal(0),
                'tax_exemption_reason_id': exemption_reason,
                'tax_exemption_amount': Decimal(0),
            }

        exemption_group = _exemption_groups[exemption_reason]

        exemption_group['broj_stavki'] += 1
        exemption_group['ukupna_cijena_osnovna'] += Decimal(stavka['ukupna_cijena_osnovna'])
        exemption_group['ukupna_cijena_rabatisana'] += Decimal(stavka['ukupna_cijena_rabatisana'])
        exemption_group['ukupna_cijena_puna'] += Decimal(stavka['ukupna_cijena_puna'])
        exemption_group['ukupna_cijena_prodajna'] += Decimal(stavka['ukupna_cijena_prodajna'])
        exemption_group['porez_iznos'] += Decimal(stavka['porez_iznos'])
        exemption_group['rabat_iznos_osnovni'] += Decimal(stavka['rabat_iznos_osnovni'])
        exemption_group['rabat_iznos_prodajni'] += Decimal(stavka['rabat_iznos_prodajni'])

        # TODO Check
        # exemption_group['credit_note_turnover_used'] += Decimal(stavka['credit_note_turnover_used'])

        # TODO Check
        # exemption_group['credit_note_turnover_remaining'] += Decimal(stavka['credit_note_turnover_remaining'])
        exemption_group['tax_exemption_amount'] += Decimal(stavka['tax_exemption_amount'])

    podaci['grupe_poreza'] = [*podaci['grupe_poreza'], *_exemption_groups.values()]
    # ------------------------------------------------------------------------------------------------------------------

    return podaci, company, operator


def create_response_from_xml_parse_exception(xml_parse_exception):
    xml_envelope = etree.Element('{%s}Envelope' % SOAP_NS, nsmap={'soap': SOAP_NS})

    etree.SubElement(xml_envelope, '{%s}Header' % SOAP_NS)

    xml_body = etree.SubElement(xml_envelope, '{%s}Body' % SOAP_NS)

    xml_fault = etree.SubElement(xml_body, f'{SOAP_NS_ESCAPED}Fault')

    xml_faultcode = etree.SubElement(xml_fault, 'faultcode')
    xml_faultcode.text = 'soap:Sender'

    xml_faultstring = etree.SubElement(xml_fault, 'faultstring')
    xml_faultstring.text = xml_parse_exception.data['description']

    xml_detail = etree.SubElement(xml_fault, 'detail')

    if 'xpath' in xml_parse_exception.data:
        xml_message = etree.SubElement(xml_detail, f'{ELAVIRINT_NS_ESCAPED}XPath', nsmap={'elavirint': ELAVIRINT_NS})
        xml_message.text = xml_parse_exception.data['xpath']

    if 'expected_elements' in xml_parse_exception.data:
        xml_expected_elements = etree.SubElement(
            xml_detail,
            f'{ELAVIRINT_NS_ESCAPED}ExpectedElements', nsmap={'elavirint': ELAVIRINT_NS})

        for xpath in xml_expected_elements.data['expected_elements']:
            xml_xpath = etree.SubElement(xml_expected_elements, f'{ELAVIRINT_NS_ESCAPED}XPath')
            xml_xpath.text = xpath

    return False, etree.tostring(xml_envelope, pretty_print=True).decode()


def create_fail_response(message):
    xml_envelope = etree.Element('{%s}Envelope' % SOAP_NS, nsmap={'soap': SOAP_NS})

    etree.SubElement(xml_envelope, '{%s}Header' % SOAP_NS)

    xml_body = etree.SubElement(xml_envelope, '{%s}Body' % SOAP_NS)

    xml_fault = etree.SubElement(xml_body, f'{SOAP_NS_ESCAPED}Fault')

    xml_faultcode = etree.SubElement(xml_fault, 'faultcode')
    xml_faultcode.text = 'soap:Sender'

    xml_faultstring = etree.SubElement(xml_fault, 'faultstring')
    xml_faultstring.text = message

    return False, etree.tostring(xml_envelope, pretty_print=True).decode()


def create_response_from_invoice(invoice):
    xml_envelope = etree.Element('{%s}Envelope' % SOAP_NS, nsmap={'soap': SOAP_NS})

    etree.SubElement(xml_envelope, '{%s}Header' % SOAP_NS)

    xml_body = etree.SubElement(xml_envelope, '{%s}Body' % SOAP_NS)

    if invoice.jikr is None:
        efi_response = faktura_opb.listaj_efi_odgovor(invoice.id)

        xml_fault = etree.SubElement(xml_body, f'{SOAP_NS_ESCAPED}Fault')

        xml_faultcode = etree.SubElement(xml_fault, 'faultcode')
        xml_faultcode.text = 'soap:Sender'

        xml_faultstring = etree.SubElement(xml_fault, 'faultstring')
        xml_faultstring.text = efi_xml.xml_error_to_string(efi_response.faultcode, lang=i18n.LOCALE_EN_US)

        return False, etree.tostring(xml_envelope, pretty_print=True).decode()
    else:
        xml_invoice = etree.SubElement(xml_body, f'{ELAVIRINT_NS_ESCAPED}Invoice', nsmap={'elavirint': ELAVIRINT_NS})

        xml_iic = etree.SubElement(xml_invoice, 'IIC')
        xml_iic.text = str(invoice.ikof)

        xml_fic = etree.SubElement(xml_invoice, 'FIC')
        xml_fic.text = str(invoice.jikr)

        xml_efi_verify_url = etree.SubElement(xml_invoice, 'EfiVerifyUrl')
        xml_efi_verify_url.text = invoice.efi_verify_url

        xml_efi_verify_url = etree.SubElement(xml_invoice, 'OrdinalNumber')
        xml_efi_verify_url.text = str(invoice.efi_ordinal_number)

        xml_efi_verify_url = etree.SubElement(xml_invoice, 'IdNumber')
        xml_efi_verify_url.text = invoice.efi_broj_fakture

        xml_document_url = etree.SubElement(xml_invoice, 'DocumentUrl')
        xml_document_url.text = \
            f'{podesavanja.HOSTNAME}/api/soap/company/{invoice.firma.pib}/invoice/{invoice.iic}/document/a4'

        return True, etree.tostring(xml_envelope, pretty_print=True).decode()
