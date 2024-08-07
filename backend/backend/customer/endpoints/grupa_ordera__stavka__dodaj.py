import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import grupa_ordera_opb 
from backend.podesavanja import podesavanja
from backend.serializers import grupa_ordera_schema 


@requires_authentication
def api__grupa_ordera__stavka__dodaj(operater, firma):
    rezultat = grupa_ordera_opb.dodaj_fakture_u_grupu_ordera(bottle.request.json, operater)
    return json.dumps(grupa_ordera_schema.dump(rezultat), **podesavanja.JSON_DUMP_OPTIONS)
