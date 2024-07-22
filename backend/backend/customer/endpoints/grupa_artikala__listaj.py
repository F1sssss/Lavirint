import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb
from backend.podesavanja import podesavanja
from backend.serializers import grupa_artikala_schema


@requires_authentication
def api__grupa_artikala__listaj(operater, firma):
    rezultat = artikal_opb.grupa_artikala__listaj(operater)
    return json.dumps(grupa_artikala_schema.dump(rezultat, many=True), **podesavanja.JSON_DUMP_OPTIONS)