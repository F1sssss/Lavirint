import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import faktura_schema


@requires_authentication
def api__frontend__invoice__create__type1(operater, firma):
    invoice_template = None
    invoice_template_id = bottle.request.query.get('invoice_template_id')
    if invoice_template_id is not None:
        invoice_template = faktura_opb.listaj_fakturu_po_idu(invoice_template_id)

        if invoice_template.tip_fakture_id != 9:
            bottle.response.status = 400
            return bottle.response

    return json.dumps({
        'invoice_template': None if invoice_template is None else faktura_schema.dump(invoice_template)
    }, **podesavanja.JSON_DUMP_OPTIONS)
