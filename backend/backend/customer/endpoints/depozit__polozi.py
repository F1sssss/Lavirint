import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.db import db
from backend.models import Depozit
from backend.opb import depozit_opb
from backend.podesavanja import podesavanja
from backend.serializers import depozit_schema


@requires_authentication
def api__depozit__polozi(operater, firma):
    danasnji_depozit = depozit_opb.listaj_danasnji_depozit(operater.naplatni_uredjaj_id)

    if danasnji_depozit is None:
        danasnji_depozit = depozit_opb.depozit__dodaj(bottle.request.json, firma, operater)
    else:
        danasnji_depozit.iznos = bottle.request.json['iznos']
        db.session.commit()

    rezultat = depozit_opb.efi_prijava_depozita(danasnji_depozit, firma)

    deposits = depozit_opb.get_todays_deposits()

    if isinstance(rezultat, Depozit):
        return json.dumps({
            'deposit': depozit_schema.dump(rezultat),
            'deposits': depozit_schema.dump(deposits, many=True)
        }, **podesavanja.JSON_DUMP_OPTIONS)
    else:
        return json.dumps(rezultat, **podesavanja.JSON_DUMP_OPTIONS)
