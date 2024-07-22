import simplejson as json

from backend.customer.auth import requires_authentication
from backend.serializers import firma_schema


@requires_authentication
def api__firma__listaj(operater, firma):
    return json.dumps(firma_schema.dump(firma))
