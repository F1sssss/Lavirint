import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import komitent_opb
from backend.podesavanja import podesavanja


@requires_authentication
def api__komitent__placanje__param_placanje_id__obrisi(operater, firma, param_placanje_id):
    placanje = komitent_opb.listaj_placanje_po_idu(param_placanje_id)
    if placanje is None:
        bottle.response.status = 400
        return bottle.response

    if placanje.firma_id != firma.id:
        bottle.response.status = 403
        return bottle.response

    komitent_opb.obrisi_placanje(param_placanje_id)

    return json.dumps('', **podesavanja.JSON_DUMP_OPTIONS)
