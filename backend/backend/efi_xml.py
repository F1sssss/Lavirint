from datetime import datetime

from lxml import etree

from backend import calc
from backend import i18n
from backend import models
from backend.models import Faktura
from backend.models import KnjiznoOdobrenje
from backend.models import KnjiznoOdobrenjeStavka
from backend.models import PaymentMethod
from backend.opb import credit_note_opb
from backend.podesavanja import podesavanja

EFI_NS = 'https://efi.tax.gov.me/fs/schema'
EFI_SIGNATURE_NS = 'http://www.w3.org/2000/09/xmldsig#'
SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'

XML_EFI_REQUEST_NSMAP = {
    None: EFI_NS,
    'ns2': EFI_SIGNATURE_NS
}

SOAP_NSMAP = {
    'SOAP-ENV': 'http://schemas.xmlsoap.org/soap/envelope/'
}

SIGNATURE_NSMAP = {
    None: EFI_SIGNATURE_NS
}

EFI_RESPONSE_SEARCH_NS = {
    'efi': EFI_NS,
    'env': SOAP_NS
}

FAULTSTRINGS_BY_LANG = {
    i18n.LOCALE_SR_LATN_ME: {
        0: 'Došlo je do izuzeća tokom ekstrakcije primljene XML poruke tokom provjere veličine.',
        1: 'Primljena XML poruka premašuje dozvoljenu veličinu.',
        2: 'Vrijeme klijenta razlikuje se od vremena servera u minutima više nego što je dozvoljeno (6 sati) ili je vrijeme u budućnosti.',  # noqa: E501
        10: 'Izuzetak se dogodio tokom ekstrakcije primljene XML poruke tokom provjere XML-a na osnovu XSD-a.',
        11: 'Neuspješna potvrda XML poruke.',
        20: 'Izuzetak dogodilo se tokom ekstrakcije primljene XML poruke tokom provjere potpisa.',
        21: 'Element „potpis” nedostaje u primljenoj XML poruci.',
        22: 'Element „XML zahtjev” nedostaje u primljenoj XML poruci.',
        23: 'Došlo je do izuzeća tokom ekstrakcije XML elementa potpisa tokom provjere potpisa.',
        24: 'Dostavljeno više od jednog XML elementa potpisa.',
        25: 'Potpisan pogrešan XML element ',
        26: 'Navedena pogrešna metoda potpisa klijenta.',
        27: 'Navedena pogrešna metoda kanonizacije ',
        28: 'Navedena pogrešna metoda izvoda.',
        29: 'Kriptografski potpis pogrešan.',
        30: 'Pogrešan proračun izvoda.',
        31: 'Pogrešan cjelokupni potpis',
        32: 'Postoji više ključnih informacija nego što je potrebno.',
        33: 'Priloženi certifikat nije certifikat vrste X509.',
        34: 'Dostavljeni certifikat nije valjan.',
        35: 'Certifikat nije izdao Registrovani CA',
        36: 'Certifikat je istekao.',
        37: 'Uporediti TIN u XML-u s TIN-om u certifikatu',
        38: 'Opozvan status certifikata ',
        39: 'Status certifikata nepoznat',
        41: 'Kod poslovne jedinice ne odnosi se na aktivnu poslovnu jedinicu (prostor) poreskog obveznika.',
        42: 'Kod softvera ne odnosi se na aktivni softver.',
        43: 'Kod održavaoca ne odnosi se na aktivnog održavaoca.',
        44: 'Status PDV-a izdavaoca ne odgovara atributu „izdavalac je obveznik PDV-a”.',
        45: '„Važi od” ne može biti u prošlosti.',
        46: '„Važi do” ne može biti u prošlosti.',
        47: '„Važi do” ne može biti prije „važi od”.',
        48: 'Aktivni ENU nije moguće ažurirati.',
        50: 'Iznos gotovine za INITIAL operaciju ne može biti negativan.',
        51: 'Iznos gotovine ne može biti nula za operaciju WITHDRAW.',
        52: 'Poreski obveznik ne postoji u Registru poreskih obveznika.',
        53: 'ENU kod klijenta ne odnosi se na registrovani ili aktivni ENU ili ENU ne pripada navedenom izdavaču.',
        54: 'Vrsta identifikacije mora biti TIN (JMB/PIB).',
        55: 'Poreski obveznik nije aktivan u registru poreskih obveznika.',
        56: 'Gotovinski depozit s operacijom INITIAL već je registrovan za tekući dan.',
        57: 'Deaktivirani ENU se ne može mijenjati.',
        58: 'Gotovinski depozit s operacijom INITIAL nije registrovan za tekući dan.',
    },
    i18n.LOCALE_EN_US: {
        0: 'An exception occurred during extraction of the received XML message during size checking.',
        1: 'The received XML message exceeds the allowed size.',
        2: 'Client time is different from server time in minutes more than allowed (6 hours) or time in the future.',
        10: 'An exception occurred during the extraction of a received XML message during an XSL-based XML check.',
        11: 'XML message verification failed.',
        20: 'The exception occurred during the extraction of the received XML message during the signature verification.',  # noqa: E501
        21: 'The "signature" element is missing in the received XML message.',
        22: 'The "XML request" element is missing in the received XML message.',
        23: 'An exception occurred during the extraction of the XML signature element during signature verification.',
        24: 'More than one XML signature element submitted.',
        25: 'Wrong XML element signed',
        26: 'The wrong client signature method was specified.',
        27: 'The wrong method of canonization is stated',
        28: 'Incorrect derivation method specified.',
        29: 'Cryptographic signature incorrect.',
        30: 'Incorrect statement budget.',
        31: 'Wrong overall signature',
        32: 'There is more key information than needed.',
        33: 'The attached certificate is not an X509 type certificate.',
        34: 'The submitted certificate is invalid.',
        35: 'The certificate was not issued by the Registered CA.',
        36: 'The certificate has expired.',
        37: 'Compare the TIN in XML with the TIN in the certificate',
        38: 'Certificate status revoked',
        39: 'Certificate status unknown',
        41: 'The business unit does not refer to the active business unit (space) of the taxpayer.',
        42: 'The software code does not apply to active software.',
        43: 'The maintenance code does not apply to the active maintainer.',
        44: 'The VAT status of the issuer does not correspond to the attribute "the issuer is a VAT payer".',
        45: '"Valid from" cannot be in the past.',
        46: '"Valid until" cannot be in the past.',
        47: '"Valid until" cannot be before "valid from".',
        48: 'The active ENU cannot be updated.',
        50: 'The amount of cash for the INITIAL operation cannot be negative.',
        51: 'The cash amount cannot be zero for a WITHDRAW operation.',
        52: 'The taxpayer does not exist in the Register of Taxpayers.',
        53: 'The client\'s ENU does not apply to a registered or active ENU or the ENU does not belong to the specified issuer.',  # noqa: E501
        54: 'The type of identification must be TIN (JMB / PIB).',
        55: 'The taxpayer is not active in the register of taxpayers.',
        56: 'Cash deposit with INITIAL operation has already been registered for the current day.',
        57: 'The deactivated ENU cannot be changed.',
        58: 'Cash deposit with INITIAL operation is not registered for the current day.',
    }
}


DEFAULT_FAULTSTRING_BY_LANG = {
    i18n.LOCALE_SR_LATN_ME: 'Servis poreske uprave nije dostupan. Molimo pokušajte ponovo kasnije.',
    i18n.LOCALE_EN_US: 'Tax administration office service is unavailable. Please try again later.'
}


def get_efi_datetime_format(value: datetime):
    dt = value.strftime('%Y-%m-%dT%H:%M:%S')
    tz = podesavanja.TIMEZONE
    return f'{dt}{tz}'


def generate_register_cash_deposit_request(
    request: models.RegisterDepositRequest,
    depozit: models.Depozit,
    firma: models.Firma
):
    xml_soap_envelope = etree.Element('{%s}Envelope' % SOAP_NS, nsmap=SOAP_NSMAP)
    xml_soap_header = etree.SubElement(xml_soap_envelope, '{%s}Header' % SOAP_NS)  # noqa: F841
    xml_soap_body = etree.SubElement(xml_soap_envelope, '{%s}Body' % SOAP_NS)

    xml_request = etree.SubElement(xml_soap_body, 'RegisterCashDepositRequest', nsmap=XML_EFI_REQUEST_NSMAP)

    xml_request.set('Id', 'Request')
    xml_request.set('Version', '1')

    xml_header = etree.SubElement(xml_request, 'Header')
    xml_header.set('SendDateTime', get_efi_datetime_format(depozit.datum_slanja))
    xml_header.set('UUID', request.uuid)

    xml_cash_depozit = etree.SubElement(xml_request, 'CashDeposit')
    xml_cash_depozit.set('CashAmt', calc.format_decimal(depozit.iznos, 2, 2))
    xml_cash_depozit.set('ChangeDateTime', get_efi_datetime_format(depozit.datum_slanja))
    xml_cash_depozit.set('IssuerTIN', firma.pib)
    xml_cash_depozit.set('Operation', 'INITIAL' if depozit.tip_depozita == 1 else 'WITHDRAW')
    xml_cash_depozit.set('TCRCode', depozit.naplatni_uredjaj.efi_kod)

    signature_placeholder = etree.SubElement(xml_request, 'Signature', nsmap=SIGNATURE_NSMAP)
    signature_placeholder.set('Id', 'placeholder')

    return xml_soap_envelope


def generate_register_invoice_request(faktura: models.Faktura, iic_signature) -> etree:
    xml_soap_envelope = etree.Element('{%s}Envelope' % SOAP_NS, nsmap=SOAP_NSMAP)
    xml_soap_header = etree.SubElement(xml_soap_envelope, '{%s}Header' % SOAP_NS)  # noqa: F841
    xml_soap_body = etree.SubElement(xml_soap_envelope, '{%s}Body' % SOAP_NS)

    xml_request = etree.SubElement(xml_soap_body, 'RegisterInvoiceRequest', nsmap=XML_EFI_REQUEST_NSMAP)

    xml_request.set('Id', 'Request')
    xml_request.set('Version', '1')

    xml_header = etree.SubElement(xml_request, 'Header')
    xml_header.set('SendDateTime', get_efi_datetime_format(faktura.datumfakture))
    xml_header.set('UUID', faktura.uuid)

    xml_invoice = etree.SubElement(xml_request, 'Invoice')
    xml_invoice.set('InvType', 'INVOICE' if faktura.tip_fakture.efi_kod == 'ORDER' else faktura.tip_fakture.efi_kod)
    xml_invoice.set('TypeOfInv', 'CASH' if faktura.is_cash else 'NONCASH')
    # xml_invoice.set('TypeOfSelfiss', '')  # min=0, max=1
    # xml_invoice.set('IsSimplifiedInv', 'false')
    xml_invoice.set('IssueDateTime', get_efi_datetime_format(faktura.datumfakture))
    xml_invoice.set('InvNum', faktura.efi_broj_fakture)
    xml_invoice.set('InvOrdNum', '%i' % faktura.efi_ordinal_number)
    xml_invoice.set('TCRCode', faktura.naplatni_uredjaj.efi_kod)
    if faktura.firma.je_poreski_obaveznik:
        xml_invoice.set('IsIssuerInVAT', 'true')
        xml_invoice.set('TotVATAmt', calc.format_decimal(faktura.porez_iznos, 2, 2))
    else:
        if faktura.tip_fakture_id in [1, 3, 4, 5, 6]:
            xml_invoice.set('TotPriceToPay', calc.format_decimal(faktura.ukupna_cijena_prodajna, 2, 2))
        xml_invoice.set('IsIssuerInVAT', 'false')
        xml_invoice.set('TaxFreeAmt', calc.format_decimal(faktura.ukupna_cijena_prodajna, 2, 2))

    # xml_invoice.set('MarkupAmt', '')  # min=0, max=1
    # xml_invoice.set('GoodsExAmt', '')  # min=0, max=1
    xml_invoice.set('TotPriceWoVAT', calc.format_decimal(faktura.ukupna_cijena_rabatisana, 2, 2))

    xml_invoice.set('TotPrice', calc.format_decimal(faktura.ukupna_cijena_prodajna, 2, 2))
    xml_invoice.set('OperatorCode', faktura.operater.kodoperatera)
    xml_invoice.set('BusinUnitCode', faktura.naplatni_uredjaj.organizaciona_jedinica.efi_kod)
    xml_invoice.set('SoftCode', podesavanja.EFI_KOD_SOFTVERA)
    xml_invoice.set('IIC', faktura.iic)
    xml_invoice.set('IICSignature', iic_signature)
    xml_invoice.set('IsReverseCharge', 'false')
    # xml_invoice.set('PayDeadline', '')  # min=0, max=1
    # xml_invoice.set('ParagonBlockNum', '')  # min=0, max=1
    xml_invoice.set('TaxPeriod', faktura.poreski_period.strftime('%m/%Y'))  # min=0, max=1

    if faktura.tip_fakture_id == Faktura.TYPE_CANCELLATION:
        xml_corrective_inv = etree.SubElement(xml_invoice, 'CorrectiveInv')
        xml_corrective_inv.set('IICRef', faktura.storno_faktura.ikof)
        xml_corrective_inv.set('IssueDateTime', get_efi_datetime_format(faktura.storno_faktura.datumfakture))
        xml_corrective_inv.set('Type', 'CORRECTIVE')

    if faktura.tip_fakture_id == Faktura.TYPE_CORRECTIVE:
        xml_corrective_inv = etree.SubElement(xml_invoice, 'CorrectiveInv')
        if faktura.korigovana_faktura is not None:
            xml_corrective_inv.set('IICRef', faktura.korigovana_faktura.ikof)
            xml_corrective_inv.set('IssueDateTime', get_efi_datetime_format(faktura.korigovana_faktura.datumfakture))
            xml_corrective_inv.set('Type', 'CORRECTIVE')
        elif faktura.corrected_credit_note is not None:
            xml_corrective_inv.set('IICRef', faktura.corrected_credit_note.ikof)
            xml_corrective_inv.set('IssueDateTime', get_efi_datetime_format(faktura.corrected_credit_note.datum_fiskalizacije))
            xml_corrective_inv.set('Type', 'CORRECTIVE')
        else:
            raise Exception('Corrective invoice element not set.')

    if faktura.tip_fakture_id == Faktura.TYPE_ERROR_CORRECTIVE:
        xml_corrective_inv = etree.SubElement(xml_invoice, 'CorrectiveInv')
        if faktura.korigovana_faktura is not None:
            xml_corrective_inv.set('IICRef', faktura.korigovana_faktura.ikof)
            xml_corrective_inv.set('IssueDateTime', get_efi_datetime_format(faktura.korigovana_faktura.datumfakture))
            xml_corrective_inv.set('Type', 'ERROR_CORRECTIVE')
        elif faktura.corrected_credit_note is not None:
            xml_corrective_inv.set('IICRef', faktura.corrected_credit_note.ikof)
            xml_corrective_inv.set('IssueDateTime', get_efi_datetime_format(faktura.corrected_credit_note.datum_fiskalizacije))
            xml_corrective_inv.set('Type', 'ERROR_CORRECTIVE')
        else:
            raise Exception('Corrective invoice element not set.')

    if faktura.tip_fakture_id == Faktura.TYPE_CUMMULATIVE and len(faktura.clanice_zbirne_fakture) > 0:
        xml_iicrefs = etree.SubElement(xml_invoice, 'IICRefs')
        for clanica_zbirne_fakture in faktura.clanice_zbirne_fakture:
            xml_iicref = etree.SubElement(xml_iicrefs, 'IICRef')
            xml_iicref.set('IIC', clanica_zbirne_fakture.ikof)
            xml_iicref.set('IssueDateTime', get_efi_datetime_format(clanica_zbirne_fakture.datumfakture))
            xml_iicref.set('Amount', calc.format_decimal(clanica_zbirne_fakture.ukupna_cijena_prodajna, 2, 2))

    # if faktura.tip_fakture_id == 1:
    #     if faktura.vrstaplacanja.id != 7 and len(faktura.fakture_djeca):
    #         xml_iicrefs = etree.SubElement(xml_invoice, 'IICRefs')
    #         for faktura_dijete in faktura.fakture_djeca:
    #             xml_iicref = etree.SubElement(xml_iicrefs, 'IICRef')
    #             xml_iicref.set('IIC', faktura_dijete.ikof)
    #             xml_iicref.set('IssueDateTime', get_efi_datetime_format(faktura_dijete.datumfakture))
    #             xml_iicref.set('Amount', calc.format_decimal(faktura_dijete.ukupna_cijena_prodajna, 2, 2))

    xml_pay_methods = etree.SubElement(xml_invoice, 'PayMethods')
    for payment_method in faktura.payment_methods:
        xml_pay_method = etree.SubElement(xml_pay_methods, 'PayMethod')
        xml_pay_method.set('Amt', calc.format_decimal(payment_method.amount, 2, 2))
        xml_pay_method.set('Type', payment_method.payment_method_type.efi_code)
        if payment_method.payment_method_type_id == 7:
            xml_pay_method.set('AdvIIC', payment_method.advance_invoice.ikof)

    if faktura.valuta.iso_4217_alfanumericki_kod != 'EUR':
        xml_currency = etree.SubElement(xml_invoice, 'Currency')
        xml_currency.set('Code', faktura.valuta.iso_4217_alfanumericki_kod)
        xml_currency.set('ExRate', calc.format_decimal(faktura.kurs_razmjene, 2, 2))  # ?-decimal

    xml_seller = etree.SubElement(xml_invoice, 'Seller')
    xml_seller.set('IDType', 'TIN')
    xml_seller.set('IDNum', faktura.firma.pib)
    xml_seller.set('Name', faktura.firma.naziv)
    xml_seller.set('Country', faktura.firma.drzave.drzava_skraceno_3)
    xml_seller.set('Town', faktura.firma.grad)
    xml_seller.set('Address', faktura.firma.adresa)

    if faktura.komitent is not None:
        xml_buyer = etree.SubElement(xml_invoice, 'Buyer')
        xml_buyer.set('IDType', faktura.komitent.tip_identifikacione_oznake.efi_kod)
        xml_buyer.set('IDNum', faktura.komitent.identifikaciona_oznaka)
        xml_buyer.set('Name', faktura.komitent.naziv)
        xml_buyer.set('Country', faktura.komitent.drzave.drzava_skraceno_3)
        xml_buyer.set('Town', faktura.komitent.grad)
        xml_buyer.set('Address', faktura.komitent.adresa)

    if len(faktura.stavke) > 0:
        xml_items = etree.SubElement(xml_invoice, 'Items')
        for faktura_stavka in faktura.stavke:
            xml_item = etree.SubElement(xml_items, 'I')
            xml_item.set('C', '%s' % faktura_stavka.sifra)
            xml_item.set('N', faktura_stavka.naziv[:50])
            xml_item.set('PA', calc.format_decimal(faktura_stavka.ukupna_cijena_prodajna, 4, 4))  # 4-decimal
            xml_item.set('PB', calc.format_decimal(faktura_stavka.ukupna_cijena_rabatisana, 4, 4))  # 4-decimal
            xml_item.set('Q', calc.format_decimal(faktura_stavka.kolicina, 2, 3))
            xml_item.set('R', calc.format_decimal(faktura_stavka.rabat_procenat, 4, 4))  # 4-decimal
            xml_item.set('U', '%s' % faktura_stavka.jedinica_mjere.naziv)
            xml_item.set('UPB', calc.format_decimal(faktura_stavka.jedinicna_cijena_osnovna, 4, 4))  # 4-decimal
            xml_item.set('UPA', calc.format_decimal(faktura_stavka.jedinicna_cijena_prodajna, 4, 4))  # 4-decimal

            if faktura_stavka.izvor_kalkulacije == 1:
                xml_item.set('RR', 'true')
            elif faktura_stavka.izvor_kalkulacije == 2:
                xml_item.set('RR', 'false')
            else:
                raise Exception('Invalid calculation type for invoice item.')

            if faktura_stavka.tax_exemption_reason_id is not None:
                xml_item.set('EX', faktura_stavka.tax_exemption_reason.efi_code)
            else:
                if faktura.firma.je_poreski_obaveznik:
                    xml_item.set('VA', calc.format_decimal(faktura_stavka.porez_iznos, 4, 4))
                    xml_item.set('VR', calc.format_decimal(faktura_stavka.porez_procenat, 4, 4))

    if faktura.firma.je_poreski_obaveznik:
        xml_same_taxes = etree.SubElement(xml_invoice, 'SameTaxes')

        for stavka_poreza in faktura.grupe_poreza:
            xml_same_tax = etree.SubElement(xml_same_taxes, 'SameTax')
            xml_same_tax.set('NumOfItems', '%i' % stavka_poreza.broj_stavki)
            xml_same_tax.set('PriceBefVAT', calc.format_decimal(stavka_poreza.ukupna_cijena_rabatisana, 2, 2))

            if stavka_poreza.tax_exemption_reason_id is None:
                xml_same_tax.set('VATRate', calc.format_decimal(stavka_poreza.porez_procenat, 2, 2))
                xml_same_tax.set('VATAmt', calc.format_decimal(stavka_poreza.porez_iznos, 2, 2))
            else:
                xml_same_tax.set('ExemptFromVAT', stavka_poreza.tax_exemption_reason.efi_code)

    signature_placeholder = etree.SubElement(xml_request, 'Signature', nsmap=SIGNATURE_NSMAP)
    signature_placeholder.set('Id', 'placeholder')

    return xml_soap_envelope


def generate_register_credit_note(credit_note: KnjiznoOdobrenje, iic_signature):
    xml_soap_envelope = etree.Element('{%s}Envelope' % SOAP_NS, nsmap=SOAP_NSMAP)
    xml_soap_header = etree.SubElement(xml_soap_envelope, '{%s}Header' % SOAP_NS)  # noqa: F841
    xml_soap_body = etree.SubElement(xml_soap_envelope, '{%s}Body' % SOAP_NS)

    xml_request = etree.SubElement(xml_soap_body, 'RegisterInvoiceRequest', nsmap=XML_EFI_REQUEST_NSMAP)

    xml_request.set('Id', 'Request')
    xml_request.set('Version', '1')

    xml_header = etree.SubElement(xml_request, 'Header')
    xml_header.set('SendDateTime', get_efi_datetime_format(credit_note.datum_fiskalizacije))
    xml_header.set('UUID', credit_note.uuid)

    xml_invoice = etree.SubElement(xml_request, 'Invoice')
    xml_invoice.set('InvType', 'CREDIT_NOTE')
    xml_invoice.set('TypeOfInv', PaymentMethod.SUBTYPE_EFI_NONCASH)

    xml_invoice.set('IssueDateTime', get_efi_datetime_format(credit_note.datum_fiskalizacije))
    xml_invoice.set('InvNum', credit_note.efi_broj_fakture)
    xml_invoice.set('InvOrdNum', '%i' % credit_note.efi_ordinal_number)
    xml_invoice.set('TCRCode', credit_note.naplatni_uredjaj.efi_kod)
    if credit_note.firma.je_poreski_obaveznik:
        xml_invoice.set('IsIssuerInVAT', 'true')
    else:
        xml_invoice.set('IsIssuerInVAT', 'false')
    # xml_invoice.set('MarkupAmt', '')  # min=0, max=1
    # xml_invoice.set('GoodsExAmt', '')  # min=0, max=1
    xml_invoice.set('TotPriceWoVAT', calc.format_decimal(-1*credit_note.return_and_discount_amount, 2, 2))

    if credit_note.firma.je_poreski_obaveznik:
        xml_invoice.set('TotVATAmt', calc.format_decimal(-1*credit_note.tax_amount, 2, 2))

    xml_invoice.set('TotPrice', calc.format_decimal(-1*credit_note.return_and_discount_amount_with_tax, 2, 2))
    xml_invoice.set('OperatorCode', credit_note.operater.kodoperatera)
    xml_invoice.set('BusinUnitCode', credit_note.naplatni_uredjaj.organizaciona_jedinica.efi_kod)
    xml_invoice.set('SoftCode', podesavanja.EFI_KOD_SOFTVERA)
    xml_invoice.set('IIC', credit_note.iic)
    xml_invoice.set('IICSignature', iic_signature)
    # xml_invoice.set('PayDeadline', '')  # min=0, max=1
    # xml_invoice.set('ParagonBlockNum', '')  # min=0, max=1
    xml_invoice.set('TaxPeriod', credit_note.poreski_period.strftime('%m/%Y'))  # min=0, max=1

    xml_pay_methods = etree.SubElement(xml_invoice, 'PayMethods')
    xml_pay_method = etree.SubElement(xml_pay_methods, 'PayMethod')
    xml_pay_method.set('Amt', calc.format_decimal(-1*credit_note.return_and_discount_amount_with_tax, 2, 2))
    xml_pay_method.set('Type', PaymentMethod.TYPE_EFI_ACCOUNT)

    if credit_note.valuta.iso_4217_alfanumericki_kod != 'EUR':
        xml_currency = etree.SubElement(xml_invoice, 'Currency')
        xml_currency.set('Code', credit_note.valuta.iso_4217_alfanumericki_kod)
        xml_currency.set('ExRate', calc.format_decimal(credit_note.kurs_razmjene, 2, 2))  # ?-decimal

    xml_seller = etree.SubElement(xml_invoice, 'Seller')
    xml_seller.set('IDType', 'TIN')
    xml_seller.set('IDNum', credit_note.firma.pib)
    xml_seller.set('Name', credit_note.firma.naziv)
    xml_seller.set('Country', credit_note.firma.drzave.drzava_skraceno_3)
    xml_seller.set('Town', credit_note.firma.grad)
    xml_seller.set('Address', credit_note.firma.adresa)

    if credit_note.komitent is not None:
        xml_buyer = etree.SubElement(xml_invoice, 'Buyer')
        xml_buyer.set('IDType', credit_note.komitent.tip_identifikacione_oznake.efi_kod)
        xml_buyer.set('IDNum', credit_note.komitent.identifikaciona_oznaka)
        xml_buyer.set('Name', credit_note.komitent.naziv)
        xml_buyer.set('Country', credit_note.komitent.drzave.drzava_skraceno_3)
        xml_buyer.set('Town', credit_note.komitent.grad)
        xml_buyer.set('Address', credit_note.komitent.adresa)

    xml_iicrefs = etree.SubElement(xml_invoice, 'IICRefs')
    for faktura in credit_note.fakture:
        xml_iicref = etree.SubElement(xml_iicrefs, 'IICRef')
        xml_iicref.set('IIC', faktura.ikof)
        xml_iicref.set('IssueDateTime', get_efi_datetime_format(faktura.datumfakture))

        # TODO: Da li ide puni iznos fakture ili samo onaj koji je iskorišćen u knjižnom odobrenju
        xml_iicref.set('Amount', calc.format_decimal(faktura.credit_note_turnover_used, 2, 2))

    iic_refs = credit_note_opb.get_iic_refs_by_id(credit_note.id)
    for iic_ref in iic_refs:
        xml_iic_ref = etree.SubElement(xml_iicrefs, 'IICRef')
        xml_iic_ref.set('IIC', iic_ref.iic)
        xml_iic_ref.set('IssueDateTime', get_efi_datetime_format(iic_ref.issue_datetime))
        xml_iic_ref.set('Amount', calc.format_decimal(iic_ref.amount_21 + iic_ref.amount_7 + iic_ref.amount_0 + iic_ref.amount_exempt, 2, 2))

    xml_approvals = etree.SubElement(xml_invoice, 'Approvals')
    for stavka in credit_note.stavke:
        xml_approval = etree.SubElement(xml_approvals, 'Approval')
        xml_approval.set('VATRate', calc.format_decimal(stavka.tax_rate, 2, 2))
        xml_approval.set('VATAmt', calc.format_decimal(-1*stavka.tax_amount, 2, 2))
        if stavka.type == KnjiznoOdobrenjeStavka.ITEM_TYPE_RETURN:
            xml_approval.set('ReturnAmt', calc.format_decimal(-1*stavka.return_amount, 2, 2))
            xml_approval.set('TotalAmt', calc.format_decimal(-1*stavka.return_amount_with_tax, 2, 2))
        elif stavka.type == KnjiznoOdobrenjeStavka.ITEM_TYPE_DISCOUNT:
            xml_approval.set('DiscountAmt', calc.format_decimal(-1*stavka.discount_amount, 2, 2))
            xml_approval.set('TotalAmt', calc.format_decimal(-1*stavka.discount_amount_with_tax, 2, 2))
        else:
            # xml_approval.set('ExemptFromVAT', '%i' % 0)
            raise Exception('Invalid item type')

    if credit_note.firma.je_poreski_obaveznik:
        xml_same_taxes = etree.SubElement(xml_invoice, 'SameTaxes')

        for grupa_poreza in credit_note.grupe_poreza:
            xml_same_tax = etree.SubElement(xml_same_taxes, 'SameTax')
            xml_same_tax.set('NumOfItems', '%i' % grupa_poreza.broj_stavki)
            xml_same_tax.set('PriceBefVAT', calc.format_decimal(-1*grupa_poreza.return_and_discount_amount, 2, 2))
            xml_same_tax.set('VATRate', calc.format_decimal(grupa_poreza.tax_rate, 2, 2))
            # xml_same_tax.set('ExemptFromVAT', '')  # min=1, max=1, but schema optional
            xml_same_tax.set('VATAmt', calc.format_decimal(-1*grupa_poreza.tax_amount, 2, 2))

    signature_placeholder = etree.SubElement(xml_request, 'Signature', nsmap=SIGNATURE_NSMAP)
    signature_placeholder.set('Id', 'placeholder')

    return xml_soap_envelope


def parse_error(xml_doc):
    elements = xml_doc.xpath('/env:Envelope/env:Body/env:Fault', namespaces=EFI_RESPONSE_SEARCH_NS)

    if len(elements) == 0:
        # Not a fault XML
        pass

    uuid = xml_doc.xpath('/env:Envelope/env:Body/env:Fault/detail/requestUUID/text()',
                         namespaces=EFI_RESPONSE_SEARCH_NS)
    if len(uuid) == 0:
        # Missing data
        pass

    faultcode = xml_doc.xpath('/env:Envelope/env:Body/env:Fault/detail/code/text()', namespaces=EFI_RESPONSE_SEARCH_NS)
    if len(faultcode) == 0:
        # Missing data
        pass

    faultstring = xml_doc.xpath('/env:Envelope/env:Body/env:Fault/faultstring/text()',
                                namespaces=EFI_RESPONSE_SEARCH_NS)
    if len(faultcode) == 0:
        # Missing data
        pass

    return uuid[0], faultcode[0], faultstring[0]


def read_register_invoice_response(xml_string):
    """

    :param xml_string:
    :return: jikr, faultcode, faultstring
    """
    xml = etree.fromstring(xml_string)

    jikr = xml.xpath('/env:Envelope/env:Body/efi:RegisterInvoiceResponse/efi:FIC/text()',
                     namespaces=EFI_RESPONSE_SEARCH_NS)
    uuid = xml.xpath('/env:Envelope/env:Body/efi:RegisterInvoiceResponse/efi:Header/@UUID',
                     namespaces=EFI_RESPONSE_SEARCH_NS)

    if len(jikr) == 0:
        uuid, faultcode, faultstring = parse_error(xml)
        return uuid, faultcode, faultstring, None

    return uuid[0], None, None, jikr[0]


def read_register_deposit_response(xml_string):
    xml = etree.fromstring(xml_string)

    fcdc = xml.xpath('/env:Envelope/env:Body/efi:RegisterCashDepositResponse/efi:FCDC/text()',
                     namespaces=EFI_RESPONSE_SEARCH_NS)
    uuid = xml.xpath('/env:Envelope/env:Body/efi:RegisterCashDepositResponse/efi:Header/@UUID',
                     namespaces=EFI_RESPONSE_SEARCH_NS)

    if len(fcdc) == 0:
        uuid, faultcode, faultstring = parse_error(xml)
        return uuid, faultcode, faultstring, None

    return uuid[0], None, None, fcdc[0]


def tostring(data):
    return etree.tostring(data, pretty_print=True, method='c14n', exclusive=True)


def xml_error_to_string(faultcode, lang='sr_Latn_ME'):
    try:
        faultcode = int(faultcode)
    except Exception:
        faultcode = None

    if lang not in FAULTSTRINGS_BY_LANG.keys():
        raise ValueError('Language "%s" is not available.' % lang)

    if lang not in DEFAULT_FAULTSTRING_BY_LANG.keys():
        raise ValueError('Language "%s" is not available.' % lang)

    texts = FAULTSTRINGS_BY_LANG.get(lang)
    faultstring = texts.get(faultcode)
    if faultstring is None:
        faultstring = DEFAULT_FAULTSTRING_BY_LANG.get(lang)

    return faultstring
