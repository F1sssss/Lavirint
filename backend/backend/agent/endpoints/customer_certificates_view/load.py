from typing import List

import bottle

from backend.agent.auth import requires_authentication
import simplejson as json

from backend.models import AgentUser
from backend.models import Firma
from backend.models import FiscalizationCertificate
from backend.opb import firma_opb


@requires_authentication
def controller(agent_user: AgentUser):
    data = bottle.request.json.copy()

    customer = firma_opb.get_company_by_id(data['customerId'])

    return json.dumps({
        "customer": dump_customer(customer),
        "certificates": dump_certificates(customer.certificates)
    })


def dump_customer(customer: Firma):
    return {
        "id": customer.id,
        "name": customer.naziv
    }


def dump_certificates(certificates: List[FiscalizationCertificate]):
    return [{
        "id": certificate.id,
        "fingerprint": certificate.fingerprint,
        "not_valid_before": certificate.not_valid_before.isoformat(),
        "not_valid_after": certificate.not_valid_after.isoformat()
    } for certificate in certificates]
