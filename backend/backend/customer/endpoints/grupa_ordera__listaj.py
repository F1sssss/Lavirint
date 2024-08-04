from decimal import Decimal

import bottle
import simplejson as json
from sqlalchemy import func

from backend.customer.auth import requires_authentication
from backend.db import db
from backend.models import OrderGrupa, OrderGrupaStavka 
from backend.opb import grupa_ordera_opb 
from backend.opb.helpers import dohvati_stranicu
from backend.podesavanja import podesavanja
from backend.serializers import grupa_ordera_schema


@requires_authentication
def api__grupa_ordera__listaj(operater, firma):
    search_query = bottle.request.query.get('upit_za_pretragu', '')

    if bottle.request.query.get('page_number') is None:
        result = grupa_ordera_opb.order_grupa_po_naplatnom_uredjaju_query(operater.naplatni_uredjaj_id,search_query).all()
        # result = order_group_schema.dump(result, many=True)
        result = serialize_order_groups(result)
    else:
        page_number = int(bottle.request.query.get('page_number', 1))
        items_per_page = int(bottle.request.query.get('items_per_page', 20))
        query = grupa_ordera_opb.order_grupa_po_naplatnom_uredjaju_query(operater.naplatni_uredjaj_id,search_query)
        result = dohvati_stranicu(query, page_number, items_per_page)
        # result['items'] = order_group_schema.dump(result['items'], many=True)
        result = serialize_response(result)
    return json.dumps(result, **podesavanja.JSON_DUMP_OPTIONS)

def serialize_order_groups(data):

    serialized_order_groups = []

    for order_group in data:
        serialized_order_groups.append(grupa_ordera_schema.dump(order_group))
    
    return serialized_order_groups

def serialize_response(paged_data):

    serialized_response = []

    for order_group in paged_data['stavke']:
        serialized_response.append(grupa_ordera_schema.dump(order_group))

    return {
        'broj_stranice': paged_data['broj_stranice'],
        'broj_stavki_po_stranici': paged_data['broj_stavki_po_stranici'],
        'stavke': serialized_response,
        'ukupan_broj_stavki': paged_data['ukupan_broj_stavki'],
    }
