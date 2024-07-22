import bottle

from backend import stampa
from backend.opb import faktura_opb
from backend.opb import soap_opb
from backend.soap_api.auth import soap_basic_auth


@soap_basic_auth
def api__soap__company__param_company_tin__invoice__param_invoice_iic__document__a4(soap_user, param_company_tin, param_invoice_iic):
    invoice = faktura_opb.get_invoice_by_company_tin_and_iic(param_company_tin, param_invoice_iic)

    if invoice is None:
        bottle.response.status = 404
        return bottle.response

    permission = soap_opb.get_soap_permission_by_user_id_and_company_id(soap_user.id, invoice.firma_id)

    if permission is None:
        bottle.response.status = 403
        return bottle.response

    return stampa.get_invoice_template_for_browser(invoice, 'a4')
