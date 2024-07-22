import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import inventory_opb
from backend.podesavanja import podesavanja
from backend.serializers import magacin_schema


@requires_authentication
def api__magacin__listaj(operater, firma):
    rezultat = inventory_opb.magacin__listaj(firma)
    return json.dumps(magacin_schema.dump(rezultat, many=True), **podesavanja.JSON_DUMP_OPTIONS)
