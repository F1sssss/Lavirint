import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb
from backend.podesavanja import podesavanja
from backend.serializers import artikal_schema


@requires_authentication
def api__artikal__listaj(operater, firma):
    rezultat = artikal_opb.artikal__listaj(firma.id)
    return json.dumps(artikal_schema.dump(rezultat, many=True), **podesavanja.JSON_DUMP_OPTIONS)
