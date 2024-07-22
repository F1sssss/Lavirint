from datetime import datetime
from datetime import timedelta

import bottle
from sqlalchemy.orm import joinedload

from backend import stampa
from backend.customer.auth import requires_authentication
from backend.db import db
from backend.models import Depozit
from backend.models import Faktura


@requires_authentication
def api__izvjestaj__zurnal__param_datum_od__param_datum_do(operater, firma, param_datum_od, param_datum_do):
    now = datetime.now()
    datum_od = datetime.strptime(param_datum_od, "%Y-%m-%dT%H:%M:%S.%fZ")
    datum_do = datetime.strptime(param_datum_do, "%Y-%m-%dT%H:%M:%S.%fZ")
    datum_do = (datum_do + timedelta(seconds=1)).replace(microsecond=0)

    fakture = db.session.query(Faktura) \
        .options(joinedload(Faktura.stavke), joinedload(Faktura.payment_methods)) \
        .filter(Faktura.status.in_([Faktura.STATUS_FISCALISATION_SUCCESS, Faktura.STATUS_CANCELLED])) \
        .filter(Faktura.naplatni_uredjaj_id == operater.naplatni_uredjaj_id) \
        .filter(Faktura.datumfakture >= datum_od, Faktura.datumfakture < datum_do) \
        .all()

    depoziti = db.session.query(Depozit) \
        .filter(Depozit.naplatni_uredjaj_id == operater.naplatni_uredjaj_id) \
        .filter(Depozit.status.in_([Depozit.STATUS_FISCALISE_SUCCESS])) \
        .filter(Depozit.datum_slanja >= datum_od, Depozit.datum_slanja < datum_do) \
        .all()

    for faktura in fakture:
        faktura.qr_kod = stampa.get_invoice_qr_code_as_datauri(faktura.efi_verify_url)

    params = {
        'fakture': fakture,
        'datum_dokumenta': now,
        'datum_od': datum_od,
        'datum_do': datum_do - timedelta(seconds=1, microseconds=0),
        'firma': firma,
        'operater': operater,
        'depoziti': depoziti,
        'naplatni_uredjaj': operater.naplatni_uredjaj
    }

    return bottle.template('backend/templates/print/zurnal.html', **params)
