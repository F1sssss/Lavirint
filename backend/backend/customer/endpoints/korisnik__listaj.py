import simplejson as json

from backend.customer.auth import requires_authentication
from backend.podesavanja import podesavanja
from backend.serializers import operater_schema


@requires_authentication
def api__korisnik__listaj(operater, firma):
    return json.dumps(operater_schema.dump(operater), **podesavanja.JSON_DUMP_OPTIONS)
