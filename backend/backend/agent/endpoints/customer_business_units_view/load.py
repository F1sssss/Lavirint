from typing import List

import bottle
import simplejson as json

from backend.agent.auth import requires_authentication
from backend.models import AgentUser
from backend.models import Firma
from backend.models import OrganizacionaJedinica
from backend.opb import firma_opb


@requires_authentication
def controller(agent_user: AgentUser):
    data = bottle.request.json.copy()

    customer = firma_opb.get_company_by_id(data['customerId'])

    organizational_units = firma_opb.get_business_units(data['customerId'])

    return json.dumps({
        "customer": dump_customer(customer),
        "organizationalUnits": dump_business_units(organizational_units)
    })


def dump_customer(customer: Firma):
    return {
        "id": customer.id,
        "name": customer.naziv
    }


def dump_business_units(organizational_units: List[OrganizacionaJedinica]):
    return [{
        "fiscalizationCode": unit.efi_kod,
        "name": unit.naziv,
        "street": unit.adresa,
        "city": unit.grad,
        "countryId": unit.drzava_id
    } for unit in organizational_units]
