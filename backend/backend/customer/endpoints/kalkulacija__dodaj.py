import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import kalkulacija_opb
from backend.podesavanja import podesavanja
from backend.serializers import kalkulacija_schema


@requires_authentication
def api__kalkulacija__dodaj(operater, firma):
    rezultat = kalkulacija_opb.kalkulacija__dodaj(bottle.request.json, firma, operater)
    return json.dumps(kalkulacija_schema.dump(rezultat), **podesavanja.JSON_DUMP_OPTIONS)