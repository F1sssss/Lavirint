import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.opb.helpers import dohvati_stranicu
from backend.podesavanja import podesavanja
from backend.serializers import invoice_view_schema


@requires_authentication
def api__profaktura__listaj(operater, firma):
    page_number = int(bottle.request.query.get('broj_stranice', 1))
    items_per_page = int(bottle.request.query.get('broj_stavki_po_stranici', 10))

    query = faktura_opb.get_invoice_templates_query(firma)

    stranica = dohvati_stranicu(query, page_number, items_per_page)
    stranica['stavke'] = invoice_view_schema.dump(stranica['stavke'], many=True)

    return json.dumps({
        'stranica': stranica,
    }, **podesavanja.JSON_DUMP_OPTIONS)
