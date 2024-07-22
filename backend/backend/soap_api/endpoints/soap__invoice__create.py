import bottle

from backend import i18n
from backend.logging import logger
from backend.models import Faktura
from backend.opb import faktura_opb
from backend.soap_api import elavirint_xml
from backend.soap_api.auth import soap_basic_auth


@soap_basic_auth
def api__soap__invoice__create(soap_user):
    try:
        invoice_type, invoice_dict, firma, operater, corrected_invoice, fiscalization_date = \
            elavirint_xml.soap_xml_to_invoice_dict(soap_user, bottle.request.body)
    except elavirint_xml.XmlParseError as xml_parse_exception:
        bottle.response.status = 400
        bottle.response.body = elavirint_xml.create_response_from_xml_parse_exception(xml_parse_exception)
        logger.exception("Error while parsing XML", extra={
            'xml': bottle.request.body.read()
        })
        return bottle.response

    if invoice_type == Faktura.TYPE_REGULAR:
        result, invoice = faktura_opb.make_regular_invoice(
            invoice_dict, firma, operater, operater.naplatni_uredjaj,
            calculate_totals=False, calculate_tax_groups=False, fiscalization_date=fiscalization_date
        )

        if result.is_success:
            is_success, output = elavirint_xml.create_response_from_invoice(invoice)
        else:
            is_success, output = elavirint_xml.create_fail_response(result.get_message(i18n.LOCALE_EN_US))

    elif invoice_type == Faktura.TYPE_CANCELLATION:
        result, corrective_invoice, _ = \
            faktura_opb.make_cancellation_invoice(corrected_invoice, operater, fiscalization_date)

        if result.is_success:
            is_success, output = elavirint_xml.create_response_from_invoice(corrective_invoice)
        else:
            is_success, output = elavirint_xml.create_fail_response(result.get_message(i18n.LOCALE_EN_US))
    elif invoice_type == Faktura.TYPE_ADVANCE:
        result, invoice = faktura_opb.make_advance_invoice(
            invoice_dict, firma, operater, operater.naplatni_uredjaj,
            calculate_totals=False, calculate_tax_groups=False, fiscalization_date=fiscalization_date
        )

        if result.is_success:
            is_success, output = elavirint_xml.create_response_from_invoice(invoice)
        else:
            is_success, output = elavirint_xml.create_fail_response(result.get_message(i18n.LOCALE_EN_US))
    elif invoice_type == Faktura.TYPE_CORRECTIVE:
        bottle.response.status = 400
        logger.error('Invalid type')
        return bottle.response
    else:
        bottle.response.status = 400
        logger.error('Invalid type')
        return bottle.response

    if is_success:
        bottle.response.status = 200
        bottle.response.body = output
    else:
        bottle.response.status = 400
        logger.error('Invalid type')
        bottle.response.body = output

    bottle.response.headers.update({
        'Content-Type': 'application/xml'
    })

    return bottle.response
