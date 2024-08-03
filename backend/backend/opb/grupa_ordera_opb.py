from decimal import Decimal
import typing as t
from sqlalchemy import exc, func

from backend.db import db
from backend.models import OrderGrupa, OrderGrupaStavka
from backend.opb.faktura_opb import listaj_fakturu_po_idu, sve_fakture_su_order 

from backend import i18n


class OrderGrupaProcessingError(Exception):

    def __init__(
            self,
            messages: t.Dict[str, str],
            instance: t.Optional[OrderGrupa] = None,
            original_exception: t.Optional[Exception] = None,
            locale: t.Optional[str] = i18n.DEFAULT_LOCALE
    ):
        self.instance = instance
        self.messages = messages
        self.original_exception = original_exception

        super(OrderGrupaProcessingError, self).__init__(self.get_message(locale))

    def get_message(self, locale: t.Optional[str] = i18n.DEFAULT_LOCALE):
        return self.messages.get(locale)



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

def order_grupa_po_id(order_grupa_id, operater):
    return db.session.query(OrderGrupa) \
        .filter(OrderGrupa.id == order_grupa_id) \
        .filter(OrderGrupa.naplatni_uredjaj_id == operater.naplatni_uredjaj_id) \
        .first()

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

def dodaj_fakture_u_grupu_ordera(order_grupa_id, podaci, operater):
    try:
        order_grupa = order_grupa_po_id(order_grupa_id, operater)

        if order_grupa is None:
            raise OrderGrupaProcessingError({
                i18n.LOCALE_EN_US: 'Order group does not exist',
                i18n.LOCALE_SR_LATN_ME: 'Grupa ordera ne postoji',
            })

        for faktura_id in podaci['fakture']:

            faktura = listaj_fakturu_po_idu(faktura_id)

            if (sve_fakture_su_order(faktura) == False):
                raise OrderGrupaProcessingError({
                    i18n.LOCALE_EN_US: 'All invoices must be in order',
                    i18n.LOCALE_SR_LATN_ME: 'Sve fakture moraju biti tipa order',
                })


            if faktura is None:
                raise OrderGrupaProcessingError({
                    i18n.LOCALE_EN_US: 'Invoice does not exist',
                    i18n.LOCALE_SR_LATN_ME: 'Faktura ne postoji',
                })

            order_grupa_stavka = OrderGrupaStavka()
            order_grupa_stavka.order_grupa_id = order_grupa_id
            order_grupa_stavka.faktura_id = faktura_id

            order_grupa.stavke.append(order_grupa_stavka)

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

def izbrisi_fakture_iz_grupe_ordera(order_grupa_id, podaci, operater):
    try:
        for faktura_id in podaci['fakture']:
            db.session.query(OrderGrupaStavka) \
                .filter(OrderGrupaStavka.order_grupa_id == order_grupa_id) \
                .filter(OrderGrupaStavka.faktura_id == faktura_id) \
                .delete()

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