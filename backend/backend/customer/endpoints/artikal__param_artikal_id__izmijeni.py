import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb
from backend.podesavanja import podesavanja
from backend.serializers import artikal_schema


@requires_authentication
def api__artikal__param_artikal_id__izmijeni(operater, firma, param_artikal_id):
    artikal = artikal_opb.artikal__po_id__izmijeni(operater.magacin_id, param_artikal_id, bottle.request.json, firma)
    return json.dumps(artikal_schema.dump(artikal), **podesavanja.JSON_DUMP_OPTIONS)
