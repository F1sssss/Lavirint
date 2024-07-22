import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.models import Depozit
from backend.opb import depozit_opb
from backend.podesavanja import podesavanja
from backend.serializers import depozit_schema


@requires_authentication
def api__depozit__podigni(operater, firma):
    rezultat = depozit_opb.depozit__podigni(bottle.request.json, firma, operater)

    deposits = depozit_opb.get_todays_deposits()

    if isinstance(rezultat, Depozit):
        return json.dumps({
            'deposit': depozit_schema.dump(rezultat),
            'deposits': depozit_schema.dump(deposits, many=True)
        }, **podesavanja.JSON_DUMP_OPTIONS)
    else:
        return json.dumps(rezultat, **podesavanja.JSON_DUMP_OPTIONS)
