import bottle

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.serializers import faktura_schema


@requires_authentication
def api__profaktura__param_profaktura_id__listaj(operater, firma, param_profaktura_id):
    invoice = faktura_opb.listaj_fakturu_po_idu(param_profaktura_id)

    if invoice.tip_fakture_id != 9:
        bottle.response.status = 400
        return bottle.response

    return faktura_schema.dump(invoice)
