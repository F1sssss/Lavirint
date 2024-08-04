import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import grupa_ordera_opb 
from backend.podesavanja import podesavanja
from backend.serializers import grupa_ordera_schema

@requires_authentication
def api__grupa_ordera__param_grupa_ordera_id__izmijeni(operater, firma, param_grupa_ordera_id):
    rezultat = grupa_ordera_opb.po_id__izmijeni(param_grupa_ordera_id, bottle.request.json, operater)
    return json.dumps(grupa_ordera_schema.dump(rezultat), **podesavanja.JSON_DUMP_OPTIONS)

