import bottle

from backend import stampa
from backend.customer.auth import requires_authentication
from backend.models import Faktura
from backend.opb import faktura_opb


@requires_authentication
def api__faktura__param_faktura_id__stampa__param_tip_stampe(operater, firma, param_faktura_id, param_tip_stampe):
    faktura = faktura_opb.listaj_fakturu_po_idu(param_faktura_id)

    if faktura is None:
        bottle.response.status = 400
        return bottle.response

    if faktura.firma_id != firma.id:
        bottle.response.status = 403
        return bottle.response

    return stampa.get_invoice_template_for_browser(faktura, param_tip_stampe)
