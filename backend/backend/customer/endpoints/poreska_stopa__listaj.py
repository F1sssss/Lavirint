import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import misc_opb
from backend.podesavanja import podesavanja
from backend.serializers import poreska_stopa_schema


@requires_authentication
def api__poreska_stopa__listaj():
    result = misc_opb.listaj_poreske_stope()
    return json.dumps(poreska_stopa_schema.dump(result, many=True), **podesavanja.JSON_DUMP_OPTIONS)