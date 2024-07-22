import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import inventory_opb
from backend.serializers import magacin_zaliha_schema


@requires_authentication
def api__firma__grupa_artikala__param_grupa_artikala_id__zaliha__listaj(operater, firma, param_grupa_artikala_id):
    rezultat = inventory_opb.listaj_zalihe_po_grupi_artikala(firma.id, param_grupa_artikala_id)
    return json.dumps(magacin_zaliha_schema.dump(rezultat, many=True))
