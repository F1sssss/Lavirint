from sqlalchemy import or_

from backend.db import db
from backend.models import Artikal
from backend.models import Magacin
from backend.models import MagacinZaliha


def magacin__listaj(firma):
    return db.session.query(Magacin) \
        .filter(Magacin.firma_id == firma.id) \
        .all()


def get_invoice_item_template_query(magacin_id, firma, is_deleted: bool, pojam_za_pretragu=None):
    query = db.session.query(MagacinZaliha) \
        .filter(MagacinZaliha.magacin.has(firma_id=firma.id)) \
        .filter(MagacinZaliha.artikal.has(Artikal.is_deleted.is_(is_deleted))) \
        .filter(MagacinZaliha.magacin_id == magacin_id)

    if pojam_za_pretragu is not None:
        query = query.filter(or_(
            MagacinZaliha.artikal.has(Artikal.naziv.contains(pojam_za_pretragu)),
            MagacinZaliha.artikal.has(Artikal.sifra.startswith(pojam_za_pretragu)),
            MagacinZaliha.artikal.has(Artikal.barkod.startswith(pojam_za_pretragu)),
        ))

    return query


def listaj_zalihe_po_grupi_artikala(firma_id, grupa_artikala_id):
    return db.session.query(MagacinZaliha) \
        .filter(Artikal.grupa_artikala.has(firma_id=firma_id)) \
        .filter(MagacinZaliha.artikal.has(grupa_artikala_id=grupa_artikala_id)) \
        .all()
