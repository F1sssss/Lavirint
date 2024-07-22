import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb
from backend.podesavanja import podesavanja
from backend.serializers import grupa_artikala_schema


@requires_authentication
def api__grupa_artikala__param_grupa_artikala_id__izmijeni(operater, firma, param_grupa_artikala_id):
    rezultat = artikal_opb.grupa_artikala__po_id__izmijeni(param_grupa_artikala_id, bottle.request.json, firma)
    return json.dumps(grupa_artikala_schema.dump(rezultat), **podesavanja.JSON_DUMP_OPTIONS)
