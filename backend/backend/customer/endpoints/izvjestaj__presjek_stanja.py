from datetime import datetime

import bottle

from backend.customer.auth import requires_authentication
from backend.opb import report_opb


@requires_authentication
def api__izvjestaj__presjek_stanja(operater, firma):
    now = datetime.now()
    datum_od = now.replace(hour=0, minute=0, second=0, microsecond=0)
    datum_do = now.replace(microsecond=999)

    rezultat = report_opb.izvjestaj__stanje(
        operater.naplatni_uredjaj,
        operater,
        firma,
        datum_od,
        datum_do,
        report_opb.REPORT_TYPE_CURRENT_STATE)

    return bottle.template('backend/templates/print/stanje.html', {
        **rezultat,
        'datum_od': datum_od,
        'datum_do': now
    })
