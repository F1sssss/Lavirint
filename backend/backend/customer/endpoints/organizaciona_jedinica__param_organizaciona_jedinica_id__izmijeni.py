import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.db import db
from backend.models import OrganizacionaJedinica
from backend.podesavanja import podesavanja


def _get_string_or_none(value):
    if value is None:
        return None

    value = value.strip()
    if len(value) == 0:
        return None

    return value


@requires_authentication
def api__organizaciona_jedinica__param_organizaciona_jedinica_id__izmijeni(operater, firma, param_organizaciona_jedinica_id):
    if operater.naplatni_uredjaj.organizaciona_jedinica.id != param_organizaciona_jedinica_id:
        bottle.response.status = 404
        return bottle.response

    organizaciona_jedinica = db.session.query(OrganizacionaJedinica).get(param_organizaciona_jedinica_id)
    if organizaciona_jedinica is None:
        bottle.response.status = 404
        return bottle.response

    data = bottle.request.json

    organizaciona_jedinica.naziv = _get_string_or_none(data.get('naziv'))
    organizaciona_jedinica.grad = data['grad']
    organizaciona_jedinica.drzava_id = data['drzava_id']
    organizaciona_jedinica.adresa = data['adresa']
    db.session.add(organizaciona_jedinica)
    db.session.commit()

    return json.dumps({
        'is_success': True,
        'message': 'Podešavanja su sačuvana'
    }, **podesavanja.JSON_DUMP_OPTIONS)
