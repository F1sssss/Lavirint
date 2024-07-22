import bottle

from backend.customer.auth import requires_authentication
from backend.opb import dospjela_faktura_opb


@requires_authentication
def api__firma__dospjela_faktura__param_dospjela_faktura_id__dokument__listaj(operater, firma, param_dospjela_faktura_id):
    if not operater.podesavanja_aplikacije.vidi_dospjele_fakture:
        bottle.response.status = 403
        return bottle.response

    dospjela_faktura = dospjela_faktura_opb.listaj_po_idu(param_dospjela_faktura_id)

    if dospjela_faktura.firma_id != firma.id:
        bottle.response.status = 403
        return bottle.response

    with open(dospjela_faktura.lokacija_dokumenta, 'rb') as file:
        bottle.response.headers.append('Content-Type', 'application/pdf')
        bottle.response.headers.append('Content-Disposition', 'attachment; filename="Račun.pdf"')
        return file.read()
