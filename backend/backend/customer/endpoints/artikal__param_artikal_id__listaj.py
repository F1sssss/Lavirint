import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb
from backend.podesavanja import podesavanja
from backend.serializers import artikal_schema


@requires_authentication
def api__artikal__param_artikal_id__listaj(operater, firma, param_artikal_id):
    rezultat = artikal_opb.artikal__po_id__listaj(firma.id, param_artikal_id)
    return json.dumps(artikal_schema.dump(rezultat), **podesavanja.JSON_DUMP_OPTIONS)
