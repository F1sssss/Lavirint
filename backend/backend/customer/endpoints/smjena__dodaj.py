import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import smjena_opb
from backend.serializers import smjena_schema


@requires_authentication
def api__smjena__otvori(operater, firma):
    rezultat = smjena_opb.smjena__otvori(firma, operater)
    return json.dumps(smjena_schema.dump(rezultat))