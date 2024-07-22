import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb
from backend.serializers import grupa_artikala_schema


@requires_authentication
def api__firma__grupa_artikala__listaj(operater, firma):
    rezultat = artikal_opb.listaj_grupe_artikala(firma.id)
    return json.dumps(grupa_artikala_schema.dumps(rezultat, many=True))
