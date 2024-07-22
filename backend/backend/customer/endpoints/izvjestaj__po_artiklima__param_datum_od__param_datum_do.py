from datetime import datetime
from datetime import timedelta

import bottle

from backend.customer.auth import requires_authentication
from backend.opb import report_opb


@requires_authentication
def api__izvjestaj__po_artiklima__param_datum_od__param_datum_do(operater, firma, param_datum_od, param_datum_do):
    now = datetime.now()
    param_datum_od = datetime.strptime(param_datum_od, "%Y-%m-%dT%H:%M:%S.%fZ")
    param_datum_do = datetime.strptime(param_datum_do, "%Y-%m-%dT%H:%M:%S.%fZ")
    param_datum_do = (param_datum_do + timedelta(seconds=1)).replace(microsecond=0)

    rezultat = report_opb.izvjestaj_po_artiklima(operater.naplatni_uredjaj_id, param_datum_od, param_datum_do)

    return bottle.template('backend/templates/print/izvjestaj_po_artiklima.html', {
        'stavke': rezultat,
        'naslov': 'Izvještaj po artiklima i uslugama',
        'datum_od': param_datum_od,
        'datum_do': param_datum_do - timedelta(seconds=1, microseconds=0),
        'datum_dokumenta': now,
        'kod_operatera': operater.kodoperatera
    })
