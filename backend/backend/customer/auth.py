import bottle

from backend.opb import operater_opb
from backend.logging import cli_logger


def requires_authentication(func):
    def wrapper(*args, **kwargs):

        print(bottle.request.session)

        if 'operater_id' not in bottle.request.session:
            bottle.response.status = 401
            return bottle.response

        operater = operater_opb.get_operator_by_id(bottle.request.session['operater_id'])
        #operater = operater_opb.get_operator_by_id(388)

        if not operater.firma.je_aktivna:
            bottle.response.status = 403
            return bottle.response

        try:
            return func(*[operater, operater.firma, *args], **kwargs)
        except Exception:
            raise

    return wrapper

