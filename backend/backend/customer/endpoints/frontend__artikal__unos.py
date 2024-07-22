import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb
from backend.serializers import grupa_artikala_schema


@requires_authentication
def api__frontend__artikal__unos(operater, firma):
    return json.dumps({
        'grupe_artikala': grupa_artikala_schema.dump(artikal_opb.listaj_grupe_artikala(firma.id), many=True)
    })
