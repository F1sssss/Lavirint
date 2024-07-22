import bottle

from backend import stampa
from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb


@requires_authentication
def api__faktura__param_faktura_id__dokument__listaj(operater, firma, param_faktura_id):
    faktura = faktura_opb.listaj_fakturu_po_idu(param_faktura_id)

    if faktura is None:
        bottle.response.status = 400
        return bottle.response

    if faktura.firma_id != firma.id:
        bottle.response.status = 403
        return bottle.response

    with open(faktura.lokacija_dokumenta, 'rb') as file:
        bottle.response.body = stampa.append_to_pdf(file.read(), firma, faktura)
        bottle.response.headers.append('Content-Type', 'application/pdf')
        bottle.response.headers.append(
            'Content-Disposition',
            'attachment; filename="Račun %s.pdf"' % faktura.efi_ordinal_number
        )
        return bottle.response