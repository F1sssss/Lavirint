from datetime import datetime

import bottle

from backend.customer.auth import requires_authentication
from backend.opb import report_opb


@requires_authentication
def api__izvjestaj__dnevni__param_datum(operater, firma, param_datum):
    param_datum = datetime.strptime(param_datum, "%Y-%m-%dT%H:%M:%S.%fZ")
    datum_od = param_datum.replace(hour=0, minute=0, second=0, microsecond=0)
    datum_do = param_datum.replace(hour=23, minute=59, second=59, microsecond=999)

    rezultat = report_opb.izvjestaj__stanje(
        operater.naplatni_uredjaj,
        operater,
        firma,
        datum_od,
        datum_do,
        report_opb.REPORT_TYPE_DAILY_REPORT)

    return bottle.template('backend/templates/print/stanje.html', {
        **rezultat,
        'datum_od': datum_od,
        'datum_do': datum_do
    })
