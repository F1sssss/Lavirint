from base64 import b64decode

import bottle
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from backend.opb import soap_opb


def soap_basic_auth(func):

    def wrapper(*args, **kwargs):
        authorization_header_value = bottle.request.headers.get('Authorization')

        if authorization_header_value is None:
            bottle.response.status = 401
            return bottle.response

        split = authorization_header_value.split(' ')

        if len(split) != 2 and split[0] != 'Basic':
            bottle.response.status = 401
            return bottle.response

        request_username, request_password = b64decode(split[1]).decode().split(':', 1)

        soap_user = soap_opb.get_soap_user_by_username(request_username)
        if soap_user is None:
            bottle.response.status = 401
            return bottle.response

        if not pbkdf2_sha256.verify(request_password, soap_user.password):
            bottle.response.status = 401
            return bottle.response

        args = [soap_user, *args]

        return func(*args, **kwargs)

    return wrapper
