import bottle

from backend.customer.auth import requires_authentication
from backend.opb import firma_opb


@requires_authentication
def api__firma__izmijeni(operater, firma):
    firma_opb.update_company_data(firma.id, bottle.request.json)
