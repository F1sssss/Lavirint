import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import invoice_processing_schema


@requires_authentication
def api__faktura__order__dodaj(operater, firma):
    podaci = bottle.request.json.copy()

    result, invoice = faktura_opb.make_order_invoice(podaci, firma, operater, operater.naplatni_uredjaj)

    data = invoice_processing_schema.dump({
        'result': result,
        'invoice': invoice
    })

    return json.dumps(data, **podesavanja.JSON_DUMP_OPTIONS)