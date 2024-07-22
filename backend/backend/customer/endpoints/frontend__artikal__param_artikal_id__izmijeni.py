import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb
from backend.serializers import artikal_schema
from backend.serializers import grupa_artikala_schema
from backend.serializers import magacin_zaliha_schema


@requires_authentication
def api__frontend__artikal__param_artikal_id__izmijeni(operater, firma, param_artikal_id):
    magacin_zaliha = artikal_opb.magacin_zaliha__po_id(operater.magacin_id, param_artikal_id)
    artikal = artikal_opb.artikal__po_id__listaj(firma.id, param_artikal_id)
    grupe_artikala = artikal_opb.listaj_grupe_artikala(firma.id)

    return json.dumps({
        'artikal': artikal_schema.dump(artikal),
        'magacin_zaliha': magacin_zaliha_schema.dump(magacin_zaliha),
        'grupe_artikala': grupa_artikala_schema.dump(grupe_artikala, many=True)
    })
