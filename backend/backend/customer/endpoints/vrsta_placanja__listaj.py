import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.db import db
from backend.models import VrstaPlacanja
from backend.podesavanja import podesavanja
from backend.serializers import vrsta_placanja_schema


@requires_authentication
def api__vrsta_placanja__listaj():
    filter_id_in = bottle.request.query.getlist('id')
    filter_id_notin = bottle.request.query.getlist('not_id')

    query = db.session.query(VrstaPlacanja) \
        .filter(VrstaPlacanja.je_aktivna.is_(True)) \
        .order_by(VrstaPlacanja.sort_value)

    if len(filter_id_in) > 0:
        query = query.filter(VrstaPlacanja.id.in_(filter_id_in))

    if len(filter_id_notin) > 0:
        query = query.filter(VrstaPlacanja.id.notin_(filter_id_notin))

    result = query.all()

    return json.dumps(vrsta_placanja_schema.dump(result, many=True), **podesavanja.JSON_DUMP_OPTIONS)
