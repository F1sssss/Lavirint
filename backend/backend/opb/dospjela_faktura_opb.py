from typing import List

from backend.db import db
from backend.models import DospjelaFaktura
from backend.models import DospjelaFakturaNotifikacija


def listaj_sve_po_firma_id(firma_id):
    return db.session.query(DospjelaFaktura) \
        .filter(DospjelaFaktura.firma_id == firma_id) \
        .all()


def listaj_notifikacije_za_operatera(operater_id):
    return db.session.query(DospjelaFakturaNotifikacija) \
        .filter(DospjelaFakturaNotifikacija.operater_id == operater_id) \
        .filter(DospjelaFakturaNotifikacija.je_vidio.is_(False)) \
        .all()


def listaj_po_idu(dospjela_faktura_id):
    return db.session.query(DospjelaFaktura) \
        .filter(DospjelaFaktura.id == dospjela_faktura_id) \
        .first()


def get_notification_by_id(notifikacija_id: int):
    return db.session.query(DospjelaFakturaNotifikacija) \
        .filter(DospjelaFakturaNotifikacija.id == notifikacija_id) \
        .first()


def get_notification_by_ids(notification_ids: List[int]):
    return db.session.query(DospjelaFakturaNotifikacija) \
        .filter(DospjelaFakturaNotifikacija.id.in_(notification_ids)) \
        .all()


def set_notifications_as_seen(notification_ids: List[int]):
    db.session.query(DospjelaFakturaNotifikacija) \
        .filter(DospjelaFakturaNotifikacija.id.in_(notification_ids)) \
        .update({
            DospjelaFakturaNotifikacija.je_vidio: True
        })
    db.session.commit()
