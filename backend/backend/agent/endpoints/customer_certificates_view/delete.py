import os

import bottle

from backend import fiskalizacija
from backend.models import AgentUser
from backend.podesavanja import podesavanja
from backend.agent.auth import requires_authentication
import simplejson as json

from backend.opb import certificate_opb


@requires_authentication
def controller(agent_user: AgentUser):
    data = bottle.request.json.copy()
    db_certificate = certificate_opb.get_certificate_by_id(data['certificateId'])
    certificate_opb.delete_certificate(db_certificate)
    os.remove(fiskalizacija.get_certificate_path(db_certificate.fingerprint))
    return json.dumps({}, **podesavanja.JSON_DUMP_OPTIONS)
