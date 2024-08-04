from decimal import Decimal
import typing as t
from sqlalchemy import exc, func

from backend.db import db
from backend.models import OrderGrupa, OrderGrupaStavka
from backend.opb.faktura_opb import listaj_fakture_po_idevima, sve_fakture_su_order 


from backend.models import OrderGrupa, PaymentMethod
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
        raise OrderGrupaProcessingError({
            i18n.LOCALE_EN_US: 'Error while adding order group',
            i18n.LOCALE_SR_LATN_ME: 'Greška prilikom dodavanja grupe ordera',
        })

def order_grupa_po_id(order_grupa_id, operater):
    return db.session.query(OrderGrupa) \
        .filter(OrderGrupa.id == order_grupa_id) \
        .filter(OrderGrupa.naplatni_uredjaj_id == operater.naplatni_uredjaj_id) \
        .first()


def order_grupa_po_naplatnom_uredjaju_query(naplatni_uredjaj_id, upit_za_pretragu):
    return db.session.query(OrderGrupa) \
        .filter(OrderGrupa.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(func.lower(OrderGrupa.naziv).like(f'%{upit_za_pretragu.lower()}%')) 
        

def po_id__izmijeni(order_grupa_id, podaci, operater):
    try:
        order_grupa = order_grupa_po_id(order_grupa_id, operater)

        if order_grupa is None:
            raise OrderGrupaProcessingError({
                i18n.LOCALE_EN_US: 'Order group does not exist',
                i18n.LOCALE_SR_LATN_ME: 'Grupa ordera ne postoji',
            })

        order_grupa.naziv = podaci['naziv']

        db.session.commit()
        return order_grupa

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        raise OrderGrupaProcessingError({
            i18n.LOCALE_EN_US: 'Error while updating order group',
            i18n.LOCALE_SR_LATN_ME: 'Greška prilikom izmjene grupe ordera',
        })


def dodaj_fakture_u_grupu_ordera(podaci, operater):
    try:
        order_grupa = order_grupa_po_id(podaci['order_grupa_id'], operater)

        if order_grupa is None:
            raise OrderGrupaProcessingError({
                i18n.LOCALE_EN_US: 'Order group does not exist',
                i18n.LOCALE_SR_LATN_ME: 'Grupa ordera ne postoji',
            })

        fakture = listaj_fakture_po_idevima(podaci['fakture'])

        if(sve_fakture_su_order(fakture) == False):
            raise OrderGrupaProcessingError({
                i18n.LOCALE_EN_US: 'All invoices must be in order',
                i18n.LOCALE_SR_LATN_ME: 'Sve fakture moraju biti tipa order',
            })

        if (order_stavka_dio_order_grupe(order_grupa, fakture, operater) == True):
            raise OrderGrupaProcessingError({
                i18n.LOCALE_EN_US: 'Invoices are already in the order group',
                i18n.LOCALE_SR_LATN_ME: 'Fakture su već u grupi ordera',
            })
            
        if fakture is None:
            raise OrderGrupaProcessingError({
                i18n.LOCALE_EN_US: 'Invoice does not exist',
                i18n.LOCALE_SR_LATN_ME: 'Faktura ne postoji',
            })

        for faktura in fakture:
            order_grupa_stavka = OrderGrupaStavka()
            order_grupa_stavka.order_grupa = order_grupa
            order_grupa_stavka.faktura = faktura

            order_grupa.stavke.append(order_grupa_stavka)

        db.session.commit()
        
        return order_grupa 

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        raise OrderGrupaProcessingError({
            i18n.LOCALE_EN_US: 'Error adding invoices to order group',
            i18n.LOCALE_SR_LATN_ME: 'Greška prilikom dodavanja faktura u grupu ordera',
        })


def izbrisi_fakture_iz_grupe_ordera( podaci, operater):
    try:
        query = db.session.query(OrderGrupaStavka) \
            .filter(OrderGrupaStavka.faktura_id.in_(podaci['fakture'])) \
            .filter(OrderGrupaStavka.order_grupa_id == podaci['order_grupa_id']) \
            .delete(synchronize_session='fetch')

        db.session.commit()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        raise OrderGrupaProcessingError({
            i18n.LOCALE_EN_US: 'Error deleting invoices from order group',
            i18n.LOCALE_SR_LATN_ME: 'Greška prilikom brisanja faktura iz grupe ordera',
        })


def listaj_order_grupe_po_stavkama(order_grupa_stavke, operater):
    return db.session.query(OrderGrupa) \
        .join(OrderGrupaStavka) \
        .filter(OrderGrupaStavka.faktura_id.in_(order_grupa_stavke)) \
        .filter(OrderGrupa.naplatni_uredjaj_id == operater.naplatni_uredjaj_id) \
        .all()


def order_stavka_dio_order_grupe(order_grupa_id,order_grupa_stavke, operater):
    if type(order_grupa_stavke) is not list:
        order_grupa_stavke_id = [order_grupa_stavke.id]
    else:
        order_grupa_stavke_id = [order_grupa_stavka.id for order_grupa_stavka in order_grupa_stavke]

    order_grupe = listaj_order_grupe_po_stavkama(order_grupa_stavke_id, operater)

    if len(order_grupe) > 0:
        return True
    else:
        return False