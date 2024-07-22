import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import komitent_opb
from backend.podesavanja import podesavanja


@requires_authentication
def api__komitent__param_komitent_id__izmijeni(operater, firma, param_komitent_id):
    rezultat = komitent_opb.po_id__izmijeni(param_komitent_id, bottle.request.json, firma)
    return json.dumps(rezultat, **podesavanja.JSON_DUMP_OPTIONS)
