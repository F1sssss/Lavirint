import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import kalkulacija_opb
from backend.opb.helpers import dohvati_stranicu
from backend.podesavanja import podesavanja
from backend.serializers import kalkulacija_schema


@requires_authentication
def api__kalkulacija__listaj(operater, firma):
    if bottle.request.query.get('broj_stranice') is None:
        rezultat = kalkulacija_opb.get_query_by_company_id(firma.id).all()
        rezultat = kalkulacija_schema.dump(rezultat, many=True)
    else:
        broj_stranice = int(bottle.request.query.get('broj_stranice', 1))
        broj_stavki_po_stranici = int(bottle.request.query.get('broj_stavki_po_stranici', 10))
        query = kalkulacija_opb.get_query_by_company_id(firma.id)
        rezultat = dohvati_stranicu(query, broj_stranice, broj_stavki_po_stranici)
        rezultat['stavke'] = kalkulacija_schema.dump(rezultat['stavke'], many=True)

    return json.dumps(rezultat, **podesavanja.JSON_DUMP_OPTIONS)
