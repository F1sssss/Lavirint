import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import komitent_opb
from backend.podesavanja import podesavanja
from backend.serializers import grupa_ordera_schema 


@requires_authentication
def api__grupa_ordera__dodaj(operater, firma):
    rezultat = komitent_opb.dodaj(bottle.request.json, operater)
    return json.dumps(grupa_ordera.dump(rezultat), **podesavanja.JSON_DUMP_OPTIONS)

