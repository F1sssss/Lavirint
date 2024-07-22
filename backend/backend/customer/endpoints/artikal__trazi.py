import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb
from backend.podesavanja import podesavanja
from backend.serializers import artikal_schema


@requires_authentication
def api__artikal__trazi(operater, firma):
    rezultat = artikal_opb.artikal__trazi(bottle.request.json['pojam'], firma)
    return json.dumps(artikal_schema.dump(rezultat, many=True), **podesavanja.JSON_DUMP_OPTIONS)
