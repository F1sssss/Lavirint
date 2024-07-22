import simplejson as json

from backend.customer.auth import requires_authentication
from backend.models import Firma
from backend.models import Operater
from backend.podesavanja import podesavanja


@requires_authentication
def controller(operater: Operater, firma: Firma):
    serialized_certificates = [{
        "id": cert.id,
        "fingerprint": cert.fingerprint,
        "not_valid_before": cert.not_valid_before.isoformat(),
        "not_valid_after": cert.not_valid_after.isoformat()
    } for cert in firma.certificates]

    return json.dumps({
        "certificates": serialized_certificates
    }, **podesavanja.JSON_DUMP_OPTIONS)
