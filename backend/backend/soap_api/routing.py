from bottle import Bottle

from backend.soap_api.endpoints.soap__company__param_company_tin__invoice__param_invoice_iic__document__a4 import (
    api__soap__company__param_company_tin__invoice__param_invoice_iic__document__a4,)
from backend.soap_api.endpoints.soap__invoice__create import (
    api__soap__invoice__create,)
from backend.soap_api.endpoints.soap_wsdl import api__soap__wsdl


def setup_soap_api_routes(app: Bottle):
    app.route('/api/soap/wsdl', 'GET', api__soap__wsdl)
    app.route('/api/soap/invoice/create', 'POST', api__soap__invoice__create)
    app.route('/api/soap/company/<param_company_tin>/invoice/<param_invoice_iic>/document/a4', 'GET', api__soap__company__param_company_tin__invoice__param_invoice_iic__document__a4)
