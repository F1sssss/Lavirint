import bottle

from backend.customer.auth import requires_authentication
from backend.db import db
from backend.models import Faktura
from backend.models import Komitent
from backend.models import KomitentPlacanje


@requires_authentication
def api__frontend__buyer__param_buyer_id__state(operater, firma, param_buyer_id):
    buyer = db.session.query(Komitent).get(param_buyer_id)

    if buyer.pibvlasnikapodatka != firma.pib:
        bottle.response.status = 400
        return bottle.response

    stavke = []
    total_dugovanje = buyer.previous_debt
    total_placanja = 0

    fakture = db.session.query(Faktura) \
        .filter(Faktura.komitent_id == param_buyer_id) \
        .filter(Faktura.status.in_([2, 4])) \
        .filter(Faktura.tip_fakture_id != 9)

    for faktura in fakture:
        stavke.append({
            'datum': faktura.datumfakture,
            'iznos': faktura.ukupna_cijena_prodajna,
            'tip': 1,
            'opis': 'Faktura %s' % faktura.efi_ordinal_number
        })
        total_dugovanje += faktura.ukupna_cijena_prodajna

    placanja = db.session.query(KomitentPlacanje).filter(KomitentPlacanje.komitent_id == param_buyer_id)
    for placanje in placanja:
        stavke.append({
            'datum': placanje.datum_placanja,
            'iznos': placanje.iznos,
            'tip': -1,
            'opis': 'Uplata %s' % placanje.datum_placanja
        })
        total_placanja += placanje.iznos

    stavke.sort(key=lambda x: x['datum'])

    if buyer.previous_debt is not None and buyer.previous_debt > 0:
        stavke.insert(0, {
            'datum': None,
            'iznos': buyer.previous_debt,
            'tip': 1,
            'opis': 'Prethodni dug'
        })
        saldo = buyer.previous_debt
    else:
        saldo = 0

    for stavka in stavke:
        stavka['saldo'] = saldo + stavka['tip'] * stavka['iznos']

    return bottle.template('backend/templates/print/kartica_kupca.html', {
        'komitent': buyer,
        'stavke': stavke,
        'total_dugovanje': total_dugovanje,
        'total_placanja': total_placanja
    })
