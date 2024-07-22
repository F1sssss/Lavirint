from datetime import datetime

import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import invoice_processing_schema


@requires_authentication
def api__faktura__param_faktura_id__storniraj(operater, firma, param_faktura_id):
    corrected_invoice = faktura_opb.listaj_fakturu_po_idu(param_faktura_id)
    if corrected_invoice is None:
        bottle.response.status = 404
        return bottle.response

    if corrected_invoice.firma.id != firma.id:
        bottle.response.status = 403
        return bottle.response

    if corrected_invoice.naplatni_uredjaj_id != operater.naplatni_uredjaj_id:
        bottle.response.status = 403
        return bottle.response

    result, corrective_invoice, _ = faktura_opb.make_cancellation_invoice(corrected_invoice, operater, datetime.now())

    if result.is_success:
        return json.dumps(invoice_processing_schema.dump({
            'result': result,
            'invoice': corrective_invoice
        }), **podesavanja.JSON_DUMP_OPTIONS)
    else:
        return json.dumps(invoice_processing_schema.dump({
            'result': result,
            'message': result.message
        }), **podesavanja.JSON_DUMP_OPTIONS)
