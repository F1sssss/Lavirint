import os

import bottle
import simplejson as json

from backend import fiskalizacija
from backend.customer.auth import requires_authentication
from backend.models import Firma
from backend.models import Operater
from backend.opb import certificate_opb
from backend.podesavanja import podesavanja


@requires_authentication
def controller(operater: Operater, firma: Firma):
    certificate_id = bottle.request.json['certificate_id']
    certificate = certificate_opb.get_certificate_by_id(certificate_id)
    if certificate is None:
        return {
            "error": "Sertifikat nije pronađen"
        }

    if certificate.owner_id != firma.id:
        return {
            "error": "Sertifikat nije pronađen"
        }

    certificate_opb.delete_certificate(certificate)

    os.remove(fiskalizacija.get_certificate_path(certificate.fingerprint))

    return json.dumps({
        "certificate_expiration_date": certificate_opb.get_expiration_date(firma)
    }, **podesavanja.JSON_DUMP_OPTIONS)
