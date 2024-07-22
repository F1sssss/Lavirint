from typing import Tuple
from typing import Union

import bottle
import simplejson as json

from backend.agent.auth import requires_authentication
from backend.logging import logger
from backend.models import AgentUser
from backend.opb import firma_opb
from backend.podesavanja import podesavanja


@requires_authentication
def controller(agent_user: AgentUser):
    post_data = bottle.request.json.copy()

    is_valid, error_message = validate_post_data(post_data)
    if not is_valid:
        logger.error(error_message)
        bottle.response.status = 400
        return bottle.response

    firma_opb.update_is_active_by_id(post_data['companyId'], post_data['newStatus'])

    return json.dumps(
        serialize_response(is_success=True, is_active=post_data['newStatus']),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def validate_post_data(post_data: dict) -> Tuple[bool, Union[str, None]]:
    company_id = post_data.get('companyId')
    if company_id is None:
        return False, 'Missing required parameter "companyId"'
    if not isinstance(company_id, int):
        return False, 'Parameter "companyId" must be integer'

    new_status = post_data.get('newStatus')
    if new_status is None:
        return False, 'Missing required parameter "newStatus"'
    if not isinstance(new_status, bool):
        return False, 'Parameter "newStatus" must be boolean'

    return True, None


def serialize_response(is_success: bool, is_active: bool):
    return {
        'isSuccess': is_success,
        'newStatus': is_active
    }
