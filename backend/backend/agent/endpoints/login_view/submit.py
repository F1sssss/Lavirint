from typing import Optional

import bottle
import simplejson as json

from backend.logging import logger
from backend.opb import agent_user_opb
from backend.podesavanja import podesavanja


def controller():
    post_data: dict = bottle.request.json.copy()

    is_valid, error_message = validate_post_data(post_data)
    if not is_valid:
        logger.error(error_message)
        bottle.response.status = 400
        return bottle.response

    agent_user = agent_user_opb.get_by_username(post_data['username'])
    if agent_user is None:
        return json.dumps(
            serialize_response(error_message="Kombinacija prijavnih podataka nije ispravna."),
            **podesavanja.JSON_DUMP_OPTIONS
        )

    if not agent_user_opb.check_password(agent_user, post_data['password']):
        return json.dumps(
            serialize_response(error_message="Kombinacija prijavnih podataka nije ispravna."),
            **podesavanja.JSON_DUMP_OPTIONS
        )

    bottle.request.session['agent_user_id'] = agent_user.id
    bottle.request.session.save()

    return json.dumps(
        serialize_response(),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def validate_post_data(post_data: dict) -> (bool, [str, None]):
    username = post_data.get('username')
    if username is None:
        return False, 'Missing required parameter "username"'

    password = post_data.get('password')
    if password is None:
        return False, 'Missing required parameter "password"'

    return True, ''


def serialize_response(error_message: Optional[str] = None):
    return {
        'errorMessage': error_message
    }
