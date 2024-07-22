from datetime import datetime

import bottle

from backend.customer.auth import requires_authentication
from backend.opb import report_opb


@requires_authentication
def api__izvjestaj__periodicni__param_datum_od__param_datum_do(operater, firma, param_datum_od, param_datum_do):
    param_datum_od = datetime.strptime(param_datum_od, "%Y-%m-%dT%H:%M:%S.%fZ")
    param_datum_do = datetime.strptime(param_datum_do, "%Y-%m-%dT%H:%M:%S.%fZ")
    param_datum_do = param_datum_do.replace(microsecond=999)
    rezultat = report_opb.izvjestaj__stanje(
        operater.naplatni_uredjaj,
        operater,
        firma,
        param_datum_od,
        param_datum_do,
        report_opb.REPORT_TYPE_PERIODIC_REPORT)

    return bottle.template('backend/templates/print/stanje.html', {
        **rezultat,
        'datum_od': param_datum_od,
        'datum_do': param_datum_do
    })
