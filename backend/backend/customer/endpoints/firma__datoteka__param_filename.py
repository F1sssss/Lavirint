from pathlib import Path

import bottle

from backend.customer.auth import requires_authentication
from backend.podesavanja import podesavanja


@requires_authentication
def api__firma__datoteka__param_filename(operater, firma, param_filename):
    root = Path(podesavanja.COMPANY_FILESTORE_PATH, firma.pib)
    return bottle.static_file(param_filename, root=root)
