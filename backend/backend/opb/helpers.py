import math
import time
import typing as t
from contextlib import contextmanager
from datetime import datetime
from datetime import timedelta
from urllib.parse import urlencode
from urllib.parse import urlunsplit

import bottle
from sqlalchemy import func
from sqlalchemy import orm

from backend import calc
from backend import efi_xml
from backend.db import db
from backend.models import Depozit
from backend.models import Drzave
from backend.models import Faktura
from backend.models import PaymentMethodType
from backend.podesavanja import podesavanja


class InvoiceFilterData:

    def __init__(self):
        self.broj_stranice = 1
        self.broj_stavki_po_stranici = 10
        self.ordinal_id = None
        self.total_price_gte = None
        self.total_price_lte = None
        self.fiscalization_date_gte = None
        self.fiscalization_date_lte = None
        self.payment_type_ids = []
        self.not_payment_type_ids = []
        self.invoice_type_ids = []
        self.not_invoice_type_ids = []
        self.client_ids = []
        self.invoice_ids = []
        self.not_invoice_ids = []
        self.statuses = []
        self.not_statuses = []

    def __str__(self):
        s = f'broj_stranice: {self.broj_stranice}\n' \
            f'broj_stavki_po_stranici: {self.broj_stavki_po_stranici}\n' \
            f'ordinal_id: {self.ordinal_id}\n' \
            f'total_price_gte: {self.total_price_gte}\n' \
            f'total_price_lte: {self.total_price_lte}\n' \
            f'fiscalization_date_gte: {self.fiscalization_date_gte}\n' \
            f'fiscalization_date_lte: {self.fiscalization_date_lte}\n' \
            f'payment_type_ids: {self.payment_type_ids}\n' \
            f'not_payment_type_ids: {self.not_payment_type_ids}\n' \
            f'invoice_type_ids: {self.invoice_type_ids}\n' \
            f'not_invoice_type_ids: {self.not_invoice_type_ids}\n' \
            f'client_ids: {self.client_ids}\n' \
            f'invoice_ids: {self.invoice_ids}\n' \
            f'not_invoice_ids: {self.not_invoice_ids}\n' \
            f'statuses: {self.statuses}\n' \
            f'not_statuses: {self.not_statuses}\n'
        return s

    @staticmethod
    def _getlist(dictionary, key):
        value = dictionary.get(key)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @staticmethod
    def load_from_dict(data):
        filters = InvoiceFilterData()
        filters.broj_stranice = int(data.get('broj_stranice', 1))
        filters.broj_stavki_po_stranici = int(data.get('broj_stavki_po_stranici', 10))
        filters.ordinal_id = data.get('ordinal_id', None)
        filters.total_price_gte = data.get('total_price_gte', None)
        filters.total_price_lte = data.get('total_price_lte', None)
        filters.fiscalization_date_gte = data.get('fiscalization_date_gte', None)
        filters.fiscalization_date_lte = data.get('fiscalization_date_lte', None)
        filters.payment_type_ids = InvoiceFilterData._getlist(data, 'payment_type_id')
        filters.not_payment_type_ids = InvoiceFilterData._getlist(data, 'not_payment_type_id')
        filters.invoice_type_ids = InvoiceFilterData._getlist(data, 'invoice_type_ids')
        filters.not_invoice_type_ids = InvoiceFilterData._getlist(data, 'not_invoice_type_ids')
        filters.client_ids = InvoiceFilterData._getlist(data, 'client_id')
        filters.invoice_ids = InvoiceFilterData._getlist(data, 'invoice_ids')
        filters.not_invoice_ids = InvoiceFilterData._getlist(data, 'not_invoice_ids')
        filters.statuses = InvoiceFilterData._getlist(data, 'statuses')
        filters.not_statuses = InvoiceFilterData._getlist(data, 'not_statuses')
        return filters

    @staticmethod
    def load_from_form_dict(data: bottle.FormsDict):
        filters = InvoiceFilterData()
        filters.broj_stranice = int(data.get('broj_stranice', 1))
        filters.broj_stavki_po_stranici = int(data.get('broj_stavki_po_stranici', 10))
        filters.ordinal_id = data.get('ordinal_id')
        filters.total_price_gte = data.get('total_price_gte')
        filters.total_price_lte = data.get('total_price_lte')
        filters.fiscalization_date_gte = data.get('fiscalization_date_gte')
        filters.fiscalization_date_lte = data.get('fiscalization_date_lte')
        filters.payment_type_ids = data.getlist('payment_type_id')
        filters.not_payment_type_ids = data.getlist('not_payment_type_id')
        filters.invoice_type_ids = data.getlist('invoice_type_ids')
        filters.not_invoice_type_ids = data.getlist('not_invoice_type_ids')
        filters.client_ids = data.getlist('client_id')
        filters.invoice_ids = data.getlist('invoice_ids')
        filters.not_invoice_ids = data.getlist('not_invoice_ids')
        filters.statuses = data.getlist('statuses')
        filters.not_statuses = data.getlist('not_statuses')
        return filters


def danas_filteri():
    now = datetime.now()
    current_day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_day_start = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return current_day_start, next_day_start


def dohvati_stranicu(query: orm.Query, broj_stranice: int = 1, broj_stavki_po_stranici: int = 10) -> t.Dict[str, t.Any]:
    return {
        "broj_stranice": broj_stranice,
        "broj_stavki_po_stranici": broj_stavki_po_stranici,
        "stavke": query.limit(broj_stavki_po_stranici).offset((broj_stranice - 1) * broj_stavki_po_stranici).all(),
        "ukupan_broj_stavki": query.order_by(None).count()
    }


def dohvati_stanje(naplatni_uredjaj_id: int):
    day_start, next_day_start = danas_filteri()

    # TODO Does filter by STATUS_STORED belong here?
    deposit_initial = db.session.query(func.sum(Depozit.iznos)) \
        .filter(Depozit.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(Depozit.datum_kreiranja >= day_start, Depozit.datum_kreiranja < next_day_start) \
        .filter(Depozit.tip_depozita == Depozit.TIP_DEPOZITA_INITIAL) \
        .filter(Depozit.status.in_([Depozit.STATUS_FISCALISE_SUCCESS])) \
        .scalar()
    if deposit_initial is None:
        deposit_initial = 0

    invoice_totals = db.session.query(func.sum(Faktura.ukupna_cijena_prodajna)) \
        .filter(Faktura.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(Faktura.datumfakture >= day_start, Faktura.datumfakture < next_day_start) \
        .filter(Faktura.status.in_([Faktura.STATUS_FISCALISATION_SUCCESS, Faktura.STATUS_CANCELLED])) \
        .filter(Faktura.tip_fakture_id.notin_([Faktura.TYPE_INVOICE_TEMPLATE])) \
        .filter(Faktura.payment_methods.any(PaymentMethodType.is_cash.is_(True))) \
        .scalar()
    if invoice_totals is None:
        invoice_totals = 0

    deposit_withdrawn = db.session.query(func.sum(Depozit.iznos)) \
        .filter(Depozit.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(Depozit.datum_kreiranja >= day_start, Depozit.datum_kreiranja < next_day_start) \
        .filter(Depozit.status == Depozit.STATUS_FISCALISE_SUCCESS) \
        .filter(Depozit.tip_depozita == Depozit.TIP_DEPOZITA_WITHDRAW) \
        .scalar()
    if deposit_withdrawn is None:
        deposit_withdrawn = 0

    return {
        'depozit': deposit_initial,
        'suma_racuna': invoice_totals,
        'isplate': deposit_withdrawn,
        'ukupno': deposit_initial - deposit_withdrawn + invoice_totals
    }


def listaj_drzavu_po_iso_kodu(iso_kod):
    return db.session.query(Drzave) \
        .filter(Drzave.drzava_skraceno_3 == iso_kod) \
        .first()


def generate_batch(query, batch_size, starting_batch):
    batch_count = math.ceil(query.count() / batch_size)
    for ii in range(starting_batch, batch_count):
        rows = query.limit(batch_size).offset(ii * batch_size).all()
        yield batch_count, ii + 1, rows


def get_efi_verify_url(invoice: Faktura, is_long):
    url_params = {}
    if is_long:
        url_params['iic'] = invoice.iic
        url_params['tin'] = invoice.firma.pib
        url_params['crtd'] = efi_xml.get_efi_datetime_format(invoice.datumfakture)
        url_params['ord'] = invoice.efi_ordinal_number
        url_params['bu'] = invoice.naplatni_uredjaj.organizaciona_jedinica.efi_kod
        url_params['cr'] = invoice.naplatni_uredjaj.efi_kod
        url_params['sw'] = podesavanja.EFI_KOD_SOFTVERA
        url_params['prc'] = calc.format_decimal(invoice.ukupna_cijena_prodajna, 2, 2)
    else:
        url_params['iic'] = invoice.iic
        url_params['tin'] = invoice.firma.pib
        url_params['crtd'] = efi_xml.get_efi_datetime_format(invoice.datumfakture)
        url_params['prc'] = calc.format_decimal(invoice.ukupna_cijena_prodajna, 2, 2)

    return urlunsplit((
        podesavanja.EFI_VERIFY_PROTOCOL,
        podesavanja.EFI_VERIFY_URL,
        '',
        urlencode(url_params),
        ''
    ))


@contextmanager
def timing():
    start = time.time()
    yield
    end = time.time()
    print(' (%s sec)' % (round(end - start, 2)))