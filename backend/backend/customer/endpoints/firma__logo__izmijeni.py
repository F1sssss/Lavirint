import os
import uuid
from pathlib import Path

import bottle

from backend.customer.auth import requires_authentication
from backend.opb import firma_opb
from backend.podesavanja import podesavanja


@requires_authentication
def api__firma__logo__izmijeni(operater, firma):
    logo_url = bottle.request.forms.get('logo_url')
    logo_file = bottle.request.files.get('logo')

    logo_filepath = firma.logo_filepath
    logo_filename = firma.logo_filename

    if logo_url is None:
        if firma.logo_filepath is not None:
            os.remove(firma.logo_filepath)
        logo_filepath = None
        logo_filename = None

    new_logo_filepath = None
    if logo_file is not None:
        _, ext = os.path.splitext(logo_file.filename)
        logo_filename = '%s%s' % (uuid.uuid4(), ext)
        logo_directory = Path(podesavanja.COMPANY_FILESTORE_PATH, firma.pib)
        logo_directory.mkdir(parents=True, exist_ok=True)
        new_logo_filepath = Path(logo_directory, logo_filename)
        while os.path.exists(new_logo_filepath):
            new_logo_filepath = Path(logo_directory, logo_filename)

        logo_file.filename = logo_filename
        logo_file.save(str(logo_directory))

        logo_filepath = new_logo_filepath
        logo_filename = os.path.basename(new_logo_filepath)

    try:
        firma_opb.update_company_logo(firma.id, logo_filepath, logo_filename)
    except Exception:
        if new_logo_filepath is not None:
            os.remove(new_logo_filepath)
        raise
