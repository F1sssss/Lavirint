from datetime import datetime

import bottle
import simplejson as json

from backend import i18n
from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import faktura_schema


@requires_authentication
def api__faktura__param_faktura_id__koriguj(operater, firma, param_faktura_id):
    korigovana_faktura = faktura_opb.listaj_fakturu_po_idu(param_faktura_id)

    if korigovana_faktura is None:
        bottle.response.status = 404
        return bottle.response

    if korigovana_faktura.firma_id != firma.id:
        bottle.response.status = 403
        return bottle.response

    if korigovana_faktura.naplatni_uredjaj_id != operater.naplatni_uredjaj_id:
        bottle.response.status = 403
        return bottle.response

    data = bottle.request.json.copy()

    result, corrective_invoice, _ = faktura_opb.make_corrective_invoice(
        operater, korigovana_faktura, data['corrected_invoice'], data['corrective_invoice'], datetime.now())

    result.locale = i18n.LOCALE_SR_LATN_ME

    if result.is_success:
        return json.dumps({
            'is_success': result.is_success,
            'message': result.message,
            'corrective_invoice': faktura_schema.dump(corrective_invoice)
        }, **podesavanja.JSON_DUMP_OPTIONS)
    else:
        return json.dumps({
            'is_success': result.is_success,
            'message': result.message
        })