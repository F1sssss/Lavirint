from decimal import Decimal

from sqlalchemy import exc, func

from backend.db import db
from backend.models import OrderGrupa, OrderGrupaStavka




def dodaj_grupu_ordera(podaci, operater):
    try:
        order_grupa = OrderGrupa()

        order_grupa.naplatni_uredjaj_id = operater.naplatni_uredjaj_id
        order_grupa.naziv = podaci['naziv']
        order_grupa.komitent_id = podaci['komitent_id']

        db.session.add(order_grupa)
        db.session.commit()
        return order_grupa

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return {
            'podaci': podaci,
            'greska': {
                'opis': str(e),
                'greska': 1
            }
        }


def order_grupa_po_naplatnom_uredjaju_query(naplatni_uredjaj_id, upit_za_pretragu):

    query = db.session.query(OrderGrupa) \
        .filter(OrderGrupa.naplatni_uredjaj_id == naplatni_uredjaj_id)

    if name is not None:
        query = query.filter(Komitent.naziv.contains(name)) \

    return query

def po_id__izmijeni(order_grupa_id, podaci, operater):
    try:
        data = {
            "naziv": podaci['naziv']
        }

        db.session.query(OrderGrupa) \
            .filter(OrderGrupa.id == order_grupa_id) \
            .filter(OrderGrupa.naplatni_uredjaj_id == operater.naplatni_uredjaj_id) \
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
            'greska': {
                'opis': str(e),
                'greska': 1
            }
        }