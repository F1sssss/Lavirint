import bottle

from backend import stampa
from backend.customer.auth import requires_authentication
from backend.opb import credit_note_opb


@requires_authentication
def api__credit_note__param_credit_note_id__document(operater, firma, credit_note_id):
    credit_note = credit_note_opb.get_credit_note_by_id(credit_note_id)

    if credit_note.firma_id != firma.id:
        bottle.response.status = 403
        return bottle.response

    if credit_note is None:
        bottle.response.status = 400
        return bottle.response

    return stampa.get_credit_note_template_for_browser(credit_note)
