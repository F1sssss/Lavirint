from datetime import datetime

from backend.db import db
from backend.models import Smjena
from backend.opb.helpers import danas_filteri


def smjena__otvori(firma, operater):
    smjena = Smjena()
    smjena.operater_id = operater.id
    smjena.datum_pocetka = datetime.now()
    smjena.firma = firma
    operater.aktivna_smjena = smjena

    db.session.add(operater)
    db.session.add(firma)
    db.session.add(smjena)
    db.session.commit()

    return smjena


def smjena__zatvori(operater):
    day_start, next_day_start = danas_filteri()

    smjena = db.session.query(Smjena) \
        .filter(Smjena.operater_id == operater.id, Smjena.datum_zavrsetka is None) \
        .filter(Smjena.datum_pocetka >= day_start, Smjena.datum_pocetka < next_day_start) \
        .first()

    smjena.datum_zavrsetka = datetime.now()

    operater.aktivna_smjena_id = None

    db.session.commit()
    return smjena
