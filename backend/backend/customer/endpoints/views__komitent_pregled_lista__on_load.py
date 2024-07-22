from decimal import Decimal

import bottle
import simplejson as json

from backend.customer.helper import PagedData
from backend.models import Komitent
from backend.opb import komitent_opb
from backend.podesavanja import podesavanja
from backend.customer.auth import requires_authentication


@requires_authentication
def views__komitent_pregled_lista__on_load(operater, firma):
    data = bottle.request.json.copy()

    search_query = data.get('query')
    page_number = int(data.get('broj_stranice'))
    items_per_page = int(data.get('broj_stavki_po_stranici'))

    db_query = komitent_opb.komitent_po_pibu_query(firma.pib, search_query)
    data = PagedData(db_query, page_number, items_per_page)

    return json.dumps(serialize_response(data), **podesavanja.JSON_DUMP_OPTIONS)


def serialize_response(paged_data: PagedData[Komitent]):
    serialized_items = []
    for item in paged_data.items:
        b = {
            'id': item.id,
            'naziv': item.naziv,
            'pdvbroj': item.pdvbroj,
            'grad': item.grad,
            'adresa': item.adresa,
            'telefon': item.telefon,
            'drzava': item.drzava,
            'identifikaciona_oznaka': item.identifikaciona_oznaka,
            'tip_identifikacione_oznake_id': None,
            'tip_identifikacione_oznake': None,
            'total_payments': komitent_opb.get_total_payments_by_id(item.id),
            'fiscalized_debt': komitent_opb.get_fiscalized_debt_by_id(item.id),
            'previous_debt': Decimal(0) if item.previous_debt is None else item.previous_debt
        }

        if item.tip_identifikacione_oznake_id is not None:
            b['tip_identifikacione_oznake_id'] = item.tip_identifikacione_oznake_id
            b['tip_identifikacione_oznake'] = {
                'id': item.tip_identifikacione_oznake.id,
                'naziv': item.tip_identifikacione_oznake.naziv
            }

        serialized_items.append(b)

    return {
        'pagedData': {
            'broj_stranice': paged_data.page_number,
            'broj_stavki_po_stranici': paged_data.items_per_page,
            'ukupan_broj_stavki': paged_data.total_items,
            'stavke': serialized_items
        }
    }
