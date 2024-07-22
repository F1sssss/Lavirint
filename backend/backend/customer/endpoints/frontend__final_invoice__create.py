import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import faktura_schema


@requires_authentication
def api__frontend__final_invoice__create(operater, firma):
    advance_invoice = None
    advance_invoice_id = bottle.request.query.get('advance_invoice_id')
    if advance_invoice_id is not None:
        advance_invoice = faktura_opb.listaj_fakturu_po_idu(advance_invoice_id)

        if advance_invoice.tip_fakture_id != 5 and advance_invoice.is_advance_invoice is not True:
            bottle.response.status = 400
            return bottle.response

    return json.dumps({
        'advance_invoice': None if advance_invoice is None else faktura_schema.dump(advance_invoice)
    }, **podesavanja.JSON_DUMP_OPTIONS)
