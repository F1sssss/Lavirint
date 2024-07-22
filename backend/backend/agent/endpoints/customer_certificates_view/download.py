import os

import bottle

from backend import fiskalizacija
from backend.models import AgentUser
from backend.agent.auth import requires_authentication

from backend.opb import certificate_opb


@requires_authentication
def controller(agent_user: AgentUser):
    data = bottle.request.json.copy()
    db_certificate = certificate_opb.get_certificate_by_id(data['certificateId'])
    filepath = fiskalizacija.get_certificate_path(db_certificate.fingerprint)
    filename = os.path.basename(filepath)
    bottle.response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return bottle.static_file(filename, root=os.path.dirname(filepath), download=filename)
