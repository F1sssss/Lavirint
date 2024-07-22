import bottle

from backend.customer.auth import requires_authentication
from backend.opb import operater_opb


@requires_authentication
def api__korisnik__izmijeni(operater, firma):
    operater_opb.operater_izmijeni(operater.id, bottle.request.json)
    return bottle.response
