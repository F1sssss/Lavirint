from decimal import Decimal

import bottle
import simplejson as json
from sqlalchemy import func

from backend.customer.auth import requires_authentication
from backend.db import db
from backend.models import Faktura, KomitentPlacanje
from backend.opb import komitent_opb
from backend.opb.helpers import dohvati_stranicu
from backend.podesavanja import podesavanja


@requires_authentication
def api__komitent__listaj(operater, firma):
    upit_za_pretragu = bottle.request.query.get('upit_za_pretragu', '')

    if bottle.request.query.get('broj_stranice') is None:
        rezultat = komitent_opb.komitent_po_pibu_query(firma.pib, upit_za_pretragu).all()
        # rezultat = komitent_schema.dump(rezultat, many=True)
        rezultat = serialize_buyers(rezultat)
    else:
        broj_stranice = int(bottle.request.query.get('broj_stranice', 1))
        broj_stavki_po_stranici = int(bottle.request.query.get('broj_stavki_po_stranici', 20))
        query = komitent_opb.komitent_po_pibu_query(firma.pib, upit_za_pretragu)
        rezultat = dohvati_stranicu(query, broj_stranice, broj_stavki_po_stranici)
        # rezultat['stavke'] = komitent_schema.dump(rezultat['stavke'], many=True)
        rezultat = serialize_response(rezultat)
    return json.dumps(rezultat, **podesavanja.JSON_DUMP_OPTIONS)


def serialize_buyers(data):
    serialized_buyers = []
    for buyer in data:
        serialized_buyer = {
            'id': buyer.id,
            'naziv': buyer.naziv,
            'pdvbroj': buyer.pdvbroj,
            'grad': buyer.grad,
            'adresa': buyer.adresa,
            'telefon': buyer.telefon,
            'drzava': buyer.drzava,
            'identifikaciona_oznaka': buyer.identifikaciona_oznaka,
            'tip_identifikacione_oznake_id': None,
            'tip_identifikacione_oznake': None,
        }

        if buyer.tip_identifikacione_oznake_id is not None:
            serialized_buyer['tip_identifikacione_oznake'] = {
                'id': buyer.tip_identifikacione_oznake.id,
                'naziv': buyer.tip_identifikacione_oznake.naziv
            }
            serialized_buyer['tip_identifikacione_oznake_id'] = buyer.tip_identifikacione_oznake_id

        serialized_buyers.append(serialized_buyer)

    return serialized_buyers


def serialize_response(paged_data: any):
    serialized_buyers = []
    for buyer in paged_data['stavke']:
        serialized_buyer = {
            'id': buyer.id,
            'naziv': buyer.naziv,
            'pdvbroj': buyer.pdvbroj,
            'grad': buyer.grad,
            'adresa': buyer.adresa,
            'telefon': buyer.telefon,
            'drzava': buyer.drzava,
            'identifikaciona_oznaka': buyer.identifikaciona_oznaka,
            'tip_identifikacione_oznake_id': None,
            'tip_identifikacione_oznake': None,
        }

        if buyer.tip_identifikacione_oznake_id is not None:
            serialized_buyer['tip_identifikacione_oznake'] = {
                'id': buyer.tip_identifikacione_oznake.id,
                'naziv': buyer.tip_identifikacione_oznake.naziv
            }
            serialized_buyer['tip_identifikacione_oznake_id'] = buyer.tip_identifikacione_oznake_id

        serialized_buyer['suma_placanja'] = komitent_opb.get_total_payments_by_id(buyer.id)
        serialized_buyer['fiscalized_debt'] = komitent_opb.get_fiscalized_debt_by_id(buyer.id)
        serialized_buyer['previous_debt'] = Decimal(0) if buyer.previous_debt is None else buyer.previous_debt
        serialized_buyers.append(serialized_buyer)

    return {
        'broj_stranice': paged_data['broj_stranice'],
        'broj_stavki_po_stranici': paged_data['broj_stavki_po_stranici'],
        'stavke': serialized_buyers,
        'ukupan_broj_stavki': paged_data['ukupan_broj_stavki'],
    }
