import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import misc_opb
from backend.serializers import tip_identifikacione_oznake_schema


@requires_authentication
def api__tip_identifikacione_oznake__listaj(operater, firma):
    tipovi_identifikacione_oznake = misc_opb.tip_identifikacione_oznake__listaj()
    return json.dumps(tip_identifikacione_oznake_schema.dump(tipovi_identifikacione_oznake, many=True))
