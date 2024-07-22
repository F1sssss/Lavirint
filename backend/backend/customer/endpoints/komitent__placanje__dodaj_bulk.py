from datetime import datetime

import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import komitent_opb
from backend.podesavanja import podesavanja


@requires_authentication
def api__komitent__placanje__dodaj_bulk(operater, firma):
    for placanje in bottle.request.json:
        komitent_id = placanje.get('komitent_id')
        if komitent_id is None:
            bottle.response.status = 400
            return bottle.response

        komitent = komitent_opb.po_id__listaj(komitent_id, firma)
        if komitent is None:
            bottle.response.status = 400
            return bottle.response

        komitent_opb.dodaj_placanje({
            'firma_id': firma.id,
            'komitent_id': komitent_id,
            'iznos': placanje['iznos'],
            'datum_placanja': datetime.fromisoformat(placanje['datum_placanja'].replace('Z', podesavanja.TIMEZONE))
        })

    return json.dumps('', **podesavanja.JSON_DUMP_OPTIONS)
