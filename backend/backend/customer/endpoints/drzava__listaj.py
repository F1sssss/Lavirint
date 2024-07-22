from typing import List

import simplejson as json

from backend.customer.auth import requires_authentication
from backend.models import Drzave
from backend.opb import misc_opb
from backend.podesavanja import podesavanja


@requires_authentication
def api__drzava__listaj(operater, firma):
    rezultat = misc_opb.listaj_drzave()
    return json.dumps(serialize_response(rezultat), **podesavanja.JSON_DUMP_OPTIONS)


def serialize_response(countries: List[Drzave]):
    serialized_countries = []
    for country in countries:
        serialized_countries.append({
            ''
        })

    return serialized_countries