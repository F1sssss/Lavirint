import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import komitent_opb
from backend.podesavanja import podesavanja
from backend.serializers import komitent_schema


@requires_authentication
def api__komitent__dodaj(operater, firma):
    rezultat = komitent_opb.dodaj(bottle.request.json, firma)
    return json.dumps(komitent_schema.dump(rezultat), **podesavanja.JSON_DUMP_OPTIONS)
