from decimal import Decimal

from sqlalchemy import exc, func

from backend.db import db
from backend.models import Komitent, Faktura
from backend.models import KomitentPlacanje


def komitent_po_pibu_query(pib, upit_za_pretragu=None):
    query = db.session.query(Komitent) \
        .filter(Komitent.pibvlasnikapodatka == pib)

    if upit_za_pretragu is not None:
        query = query.filter(Komitent.naziv.contains(upit_za_pretragu)) \

    return query


def dodaj(podaci, firma):
    try:
        komitent = Komitent()
        komitent.pibvlasnikapodatka = firma.pib

        komitent.drzava = podaci['drzava']
        komitent.adresa = podaci['adresa']
        komitent.email = podaci.get('email')
        komitent.grad = podaci['grad']
        komitent.identifikaciona_oznaka = podaci['identifikaciona_oznaka']
        komitent.napomena = podaci.get('napomena')
        komitent.naziv = podaci['naziv']
        komitent.pdvbroj = podaci.get('pdvbroj')
        komitent.telefon = podaci.get('telefon')
        komitent.tip_identifikacione_oznake_id = podaci['tip_identifikacione_oznake_id']
        komitent.ziroracun = podaci.get('ziroracun')
        komitent.show_total_debt = podaci.get('show_total_debt')
        komitent.previous_debt = podaci.get('previous_debt')

        db.session.add(komitent)
        db.session.commit()
        return komitent
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return {
            'podaci': podaci,
            'greska': {
                'opis': str(e),
                'greska': 1
            }
        }


def po_id__izmijeni(komitent_id, podaci, firma):
    try:
        data = {
            "drzava": podaci['drzava'],
            "adresa": podaci['adresa'],
            "email": podaci.get('email'),
            "grad": podaci['grad'],
            "identifikaciona_oznaka": podaci['identifikaciona_oznaka'],
            "napomena": podaci.get('napomena'),
            "naziv": podaci['naziv'],
            "pdvbroj": podaci.get('pdvbroj'),
            "telefon": podaci.get('telefon'),
            "tip_identifikacione_oznake_id": podaci['tip_identifikacione_oznake_id'],
            "ziroracun": podaci.get('ziroracun'),
            "show_total_debt": podaci.get('show_total_debt'),
            "previous_debt": podaci.get('previous_debt')
        }

        db.session.query(Komitent) \
            .filter(Komitent.id == komitent_id) \
            .filter(Komitent.pibvlasnikapodatka == firma.pib) \
            .update(data)

        db.session.commit()

        return {
            'podaci': podaci,
            'greska': 0
        }
    except exc.SQLAlchemyError as e:
        db.session.rollback()

        return {
            'podaci': podaci,
            'greska': 1,
            'opisgreske': str(e)
        }


def po_identifikaciji__listaj(tip_identifikacione_oznake_id, identifikaciona_oznaka, pibvlasnikapodatka):
    return db.session.query(Komitent) \
        .filter(Komitent.tip_identifikacione_oznake_id == tip_identifikacione_oznake_id) \
        .filter(Komitent.identifikaciona_oznaka == identifikaciona_oznaka) \
        .filter(Komitent.pibvlasnikapodatka == pibvlasnikapodatka) \
        .first()


def po_id__listaj(komitent_id, firma):
    return db.session.query(Komitent) \
        .filter(Komitent.pibvlasnikapodatka == firma.pib, Komitent.id == komitent_id) \
        .first()


def get_by_id(komitent_id) -> Komitent:
    return db.session.query(Komitent) \
        .filter(Komitent.id == komitent_id) \
        .first()


def listaj_placanje_po_idu(placanje_id):
    return db.session.query(KomitentPlacanje).filter(KomitentPlacanje.id == placanje_id).first()


def dodaj_placanje(podaci):
    placanje = KomitentPlacanje()
    placanje.firma_id = podaci['firma_id']
    placanje.komitent_id = podaci['komitent_id']
    placanje.iznos = podaci['iznos']
    placanje.datum_placanja = podaci['datum_placanja']

    db.session.add(placanje)
    db.session.commit()


def obrisi_placanje(placanje_id):
    db.session.query(KomitentPlacanje) \
        .filter(KomitentPlacanje.id == placanje_id) \
        .delete()

    db.session.commit()


def get_fiscalized_debt_by_id(buyer_id: int):
    fiscalized_debt = db.session.query(func.sum(Faktura.ukupna_cijena_prodajna)) \
        .filter(Faktura.status.in_([Faktura.STATUS_FISCALISATION_SUCCESS, Faktura.STATUS_CANCELLED])) \
        .filter(Faktura.tip_fakture_id.in_([Faktura.TYPE_REGULAR, Faktura.TYPE_CANCELLATION, Faktura.TYPE_CORRECTIVE])) \
        .filter(Faktura.komitent_id == buyer_id) \
        .scalar()
    return Decimal(0) if fiscalized_debt is None else fiscalized_debt


def get_total_payments_by_id(buyer_id: int):
    total_payments = db.session.query(func.sum(KomitentPlacanje.iznos)) \
        .filter(KomitentPlacanje.komitent_id == buyer_id) \
        .scalar()
    return Decimal(0) if total_payments is None else total_payments