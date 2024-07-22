import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import dospjela_faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import dospjela_faktura_schema


@requires_authentication
def api__firma__dospjela_faktura__listaj(operater, firma):
    if not operater.podesavanja_aplikacije.vidi_dospjele_fakture:
        bottle.response.status = 403
        return bottle.response

    dospjele_fakture = dospjela_faktura_opb.listaj_sve_po_firma_id(firma.id)

    return json.dumps(dospjela_faktura_schema.dump(dospjele_fakture, many=True), **podesavanja.JSON_DUMP_OPTIONS)