import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import faktura_schema


@requires_authentication
def api__faktura__param_faktura_id__listaj(operater, firma, param_faktura_id):
    faktura = faktura_opb.listaj_fakturu_po_idu(param_faktura_id)

    if faktura.firma_id != firma.id:
        bottle.response.status = 403
        return bottle.response

    return json.dumps(faktura_schema.dump(faktura), **podesavanja.JSON_DUMP_OPTIONS)
