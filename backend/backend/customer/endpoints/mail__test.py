import bottle
import simplejson as json

from backend.core import mailing
from backend.podesavanja import podesavanja


def api__mail__test():
    is_success = mailing.test_smtp_connection(
        host=bottle.request.json.get('smtp_host'),
        port=bottle.request.json.get('smtp_port'),
        username=bottle.request.json.get('smtp_username'),
        password=bottle.request.json.get('smtp_password')
    )

    return json.dumps({'is_success': is_success}, **podesavanja.JSON_DUMP_OPTIONS)
