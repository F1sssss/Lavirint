from datetime import datetime

import bottle
import pytz
import simplejson as json

from backend import i18n
from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.opb.faktura_opb import InvoiceProcessingException
from backend.podesavanja import podesavanja
from backend.serializers import faktura_schema


@requires_authentication
def api__profaktura__dodaj(operater, firma):
    podaci = bottle.request.json.copy()
    podaci['datumfakture'] = datetime.now(pytz.timezone('Europe/Podgorica')).isoformat()

    try:
        invoice = faktura_opb.create_invoice_template(podaci, firma, operater, operater.naplatni_uredjaj)
    except InvoiceProcessingException as exception:
        return json.dumps({
            'is_success': False,
            'message': exception.messages[i18n.LOCALE_SR_LATN_ME]
        })
    except Exception:
        return json.dumps({
            'is_success': False,
            'message': 'Došlo je do nepredviđene greške. Molimo kontaktirajte tehničku podršku.'
        })

    return json.dumps({
        'is_success': True,
        'message': 'Predračun je sačuvan.',
        'invoice': faktura_schema.dump(invoice)
    }, **podesavanja.JSON_DUMP_OPTIONS)
