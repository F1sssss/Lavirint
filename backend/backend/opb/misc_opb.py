from typing import List

from backend.db import db
from backend.models import Drzave
from backend.models import JedinicaMjere
from backend.models import PoreskaStopa
from backend.models import TipIdentifikacioneOznake
from backend.models import Valuta


def listaj_jedinicu_mjere_po_nazivu(firma_id, naziv):
    return db.session.query(JedinicaMjere) \
        .filter(JedinicaMjere.firma_id == firma_id) \
        .filter(JedinicaMjere.naziv == naziv) \
        .first()


def tip_identifikacione_oznake__listaj():
    return db.session.query(TipIdentifikacioneOznake) \
        .filter(TipIdentifikacioneOznake.id.in_([1, 2, 3, 4, 6])) \
        .all()


def get_currency_by_id(currency_id: int) -> Valuta:
    return db.session.query(Valuta).filter(Valuta.id == currency_id).first()


def valuta__listaj():
    return db.session.query(Valuta).all()


def listaj_valutu_po_iso_kodu(valuta_iso_kod):
    return db.session.query(Valuta) \
        .filter(Valuta.iso_4217_alfanumericki_kod == valuta_iso_kod) \
        .first()


def listaj_poreske_stope():
    return db.session.query(PoreskaStopa).all()


def listaj_drzave() -> List[Drzave]:
    return db.session.query(Drzave).all()


def get_country_by_id(country_id: int) -> Drzave:
    return db.session.get(Drzave, country_id)


def listaj_tipove_identifikacione_oznake():
    return db.session.query(TipIdentifikacioneOznake).all()
