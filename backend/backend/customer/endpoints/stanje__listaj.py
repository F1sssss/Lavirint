import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import depozit_opb
from backend.opb.helpers import dohvati_stanje
from backend.podesavanja import podesavanja
from backend.serializers import stanje_odgovor_schema


@requires_authentication
def api__stanje__listaj(operater, firma):
    sume_stanja = dohvati_stanje(operater.naplatni_uredjaj_id)
    danasnji_depozit = depozit_opb.listaj_danasnji_depozit(operater.naplatni_uredjaj_id)

    return json.dumps(stanje_odgovor_schema.dump({
        'depozit': sume_stanja['depozit'],
        'suma_racuna': sume_stanja['suma_racuna'],
        'isplate': sume_stanja['isplate'],
        'ukupno': sume_stanja['ukupno'],
        'danasnji_depozit': None if danasnji_depozit is None else danasnji_depozit
    }), **podesavanja.JSON_DUMP_OPTIONS)
