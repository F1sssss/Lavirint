import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import invoice_processing_schema


@requires_authentication
def api__final_invoice__create(operater, firma):
    data = bottle.request.json.copy()

    result, final_invoice = faktura_opb.make_final_invoice(
        firma, operater, operater.naplatni_uredjaj,
        final_invoice_data=data['final_invoice'],
        corrected_advance_invoice_data=data['advance_invoice'],
        corrective_for_advance_data=data['corrective_invoice'])

    if result.is_success:
        return json.dumps(invoice_processing_schema.dump({
            'result': result,
            'invoice': final_invoice
        }), **podesavanja.JSON_DUMP_OPTIONS)
    else:
        return json.dumps(invoice_processing_schema.dump({
            'result': result,
            'message': result.message
        }), **podesavanja.JSON_DUMP_OPTIONS)
