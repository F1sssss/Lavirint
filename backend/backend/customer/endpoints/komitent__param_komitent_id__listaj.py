import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import komitent_opb
from backend.podesavanja import podesavanja
from backend.serializers import komitent_schema


@requires_authentication
def api__komitent__param_komitent_id__listaj(operater, firma, param_komitent_id):
    rezultat = komitent_opb.po_id__listaj(param_komitent_id, firma)
    return json.dumps(komitent_schema.dump(rezultat), **podesavanja.JSON_DUMP_OPTIONS)
