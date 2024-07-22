import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import jedinica_mjere_schema


@requires_authentication
def api__jedinica_mjere__listaj(operater, firma):
    rezultat = faktura_opb.jedinica_mjere__listaj(firma)
    return json.dumps(jedinica_mjere_schema.dump(rezultat, many=True), **podesavanja.JSON_DUMP_OPTIONS)
