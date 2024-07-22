import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import inventory_opb
from backend.opb.helpers import dohvati_stranicu
from backend.podesavanja import podesavanja
from backend.serializers import magacin_zaliha_schema


@requires_authentication
def api__magacin__param_magacin_id__lager__listaj(operater, firma, param_magacin_id):
    if operater.magacin_id != param_magacin_id:
        bottle.response.status = 401
        return bottle.response

    pojam_za_pretragu = bottle.request.query.get('pojam_za_pretragu', '')

    if bottle.request.query.get('broj_stranice') is None:
        rezultat = inventory_opb.get_invoice_item_template_query(param_magacin_id, firma, False, pojam_za_pretragu).all()
        return json.dumps(magacin_zaliha_schema.dump(rezultat, many=True), **podesavanja.JSON_DUMP_OPTIONS)
    else:
        try:
            broj_stranice = int(bottle.request.query.get('broj_stranice'))
            broj_stavki_po_stranici = int(bottle.request.query.get('broj_stavki_po_stranici', 10))
            query = inventory_opb.get_invoice_item_template_query(param_magacin_id, firma, False, pojam_za_pretragu)
            rezultat = dohvati_stranicu(query, broj_stranice, broj_stavki_po_stranici)
            rezultat['stavke'] = magacin_zaliha_schema.dump(rezultat['stavke'], many=True)
            return json.dumps(rezultat, **podesavanja.JSON_DUMP_OPTIONS)
        except TypeError:
            bottle.response.status = 400
