import os
import uuid
from pathlib import Path

import bottle

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja


@requires_authentication
def api__faktura__param_faktura_id__dokument__upload(operater, firma, faktura_id):
    faktura = faktura_opb.listaj_fakturu_po_idu(faktura_id)

    if faktura is None:
        bottle.response.status = 400
        return bottle.response

    if faktura.firma_id != firma.id:
        bottle.response.status = 403
        return bottle.response

    document = bottle.request.files.get('dokument')

    _, ext = os.path.splitext(document.filename)
    document_filename = '%s%s' % (uuid.uuid4(), ext)
    document_directory = Path(podesavanja.COMPANY_FILESTORE_PATH, firma.pib)
    document_directory.mkdir(parents=True, exist_ok=True)

    document_filepath = Path(document_directory, document_filename)
    while os.path.exists(document_filepath):
        document_filepath = Path(document_directory, document_filename)

    document.filename = document_filename
    document.save(str(document_directory))

    faktura.lokacija_dokumenta = document_filepath
    db.session.add(faktura)
    db.session.commit()

    return bottle.response
