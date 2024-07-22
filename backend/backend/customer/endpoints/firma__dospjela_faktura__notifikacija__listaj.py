from typing import List

import simplejson as json

from backend.customer.auth import requires_authentication
from backend.models import DospjelaFakturaNotifikacija
from backend.opb import dospjela_faktura_opb
from backend.podesavanja import podesavanja


@requires_authentication
def api__firma__dospjela_faktura__notifikacija__listaj(operater, firma):
    if not operater.podesavanja_aplikacije.vidi_dospjele_fakture:
        return json.dumps({
            'notifications': []
        }, **podesavanja.JSON_DUMP_OPTIONS)

    notifikacije = dospjela_faktura_opb.listaj_notifikacije_za_operatera(operater.id)

    return json.dumps(
        serialize_response(notifikacije),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def serialize_response(notifications: List[DospjelaFakturaNotifikacija]):
    serialized_notifications = []
    for notification in notifications:
        serialized_notifications.append({
            'id': notification.id,
            'dueInvoice': {
                'id': notification.dospjela_faktura.id,
                'description': notification.dospjela_faktura.opis,
                'link': f'/api/customer/firma/dospjela_faktura/{notification.dospjela_faktura.id}/dokument/listaj'
            }
        })

    return {
        'notifications': serialized_notifications
    }
