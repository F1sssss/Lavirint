from datetime import datetime

from backend.db import db
from backend.models import Kalkulacija
from backend.models import KalkulacijaStavka
from backend.models import MagacinRedniBrojKalkulacije
from backend.models import MagacinZaliha
from backend.podesavanja import podesavanja


def get_query_by_company_id(firma_id):
    return db.session.query(Kalkulacija) \
        .filter(Kalkulacija.magacin.has(firma_id=firma_id)) \
        .order_by(Kalkulacija.id.desc())


def kalkulacija__dodaj(podaci, firma, operater):
    now = datetime.now()

    kalkulacija = Kalkulacija()
    kalkulacija.datum_kalkulacije = now
    kalkulacija.operater_id = operater.id
    kalkulacija.firma_id = firma.id
    kalkulacija.magacin_id = podaci.get('magacin_id')
    kalkulacija.dobavljac_id = podaci.get('dobavljac_id')

    _broj_ulazne_fakture = podaci.get('broj_ulazne_fakture')
    if _broj_ulazne_fakture is not None and len(_broj_ulazne_fakture) > 0:
        kalkulacija.broj_ulazne_fakture = _broj_ulazne_fakture

    _datum_ulazne_fakture = podaci.get('datum_ulazne_fakture')
    if _datum_ulazne_fakture is not None:
        kalkulacija.datum_ulazne_fakture = datetime.fromisoformat(
            _datum_ulazne_fakture.replace('Z', podesavanja.TIMEZONE))

    session_redni_broj, redni_broj_kalkulacije = dohvati_redni_broj_kalkulacije(kalkulacija.magacin_id, now.year)
    redni_broj_kalkulacije.redni_broj += 1
    kalkulacija.redni_broj_kalkulacije = redni_broj_kalkulacije.redni_broj

    for stavka in podaci['stavke']:
        kalkulacija_stavka = KalkulacijaStavka()
        kalkulacija_stavka.artikal_id = stavka['artikal_id']
        kalkulacija_stavka.kolicina = stavka['kolicina']
        kalkulacija.stavke.append(kalkulacija_stavka)

        zaliha = db.session.query(MagacinZaliha) \
            .filter(MagacinZaliha.artikal_id == kalkulacija_stavka.artikal_id) \
            .filter(MagacinZaliha.magacin_id == kalkulacija.magacin_id) \
            .first()

        zaliha.raspoloziva_kolicina += kalkulacija_stavka.kolicina
        db.session.add(zaliha)

    db.session.add(kalkulacija)
    db.session.commit()
    session_redni_broj.commit()

    return kalkulacija


def dohvati_redni_broj_kalkulacije(magacin_id, godina):
    session_redni_broj = db.create_session()

    redni_broj_kalkulacije = db.session.query(MagacinRedniBrojKalkulacije) \
        .filter(MagacinRedniBrojKalkulacije.magacin_id == magacin_id) \
        .filter(MagacinRedniBrojKalkulacije.godina == godina) \
        .with_for_update() \
        .first()

    if redni_broj_kalkulacije is None:
        # Potreban commit zato što postojeći lock onemogućava dodavanje nove stavke
        session_redni_broj.commit()

        redni_broj_kalkulacije = MagacinRedniBrojKalkulacije()
        redni_broj_kalkulacije.magacin_id = magacin_id
        redni_broj_kalkulacije.godina = godina
        redni_broj_kalkulacije.redni_broj = 0
        db.session.add(redni_broj_kalkulacije)
        db.session.commit()

        redni_broj_kalkulacije = session_redni_broj.query(MagacinRedniBrojKalkulacije) \
            .with_for_update() \
            .get(redni_broj_kalkulacije.id)

    return session_redni_broj, redni_broj_kalkulacije
