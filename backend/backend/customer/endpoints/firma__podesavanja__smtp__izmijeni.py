import bottle

from backend.core import mailing
from backend.customer.auth import requires_authentication
from backend.db import db


@requires_authentication
def api__firma__podesavanja__smtp__izmijeni(operater, firma):
    is_smtp_active = bottle.request.json.get('smtp_active')

    if is_smtp_active:
        is_success = mailing.test_smtp_connection(
            host=bottle.request.json.get('smtp_host'),
            port=bottle.request.json.get('smtp_port'),
            username=bottle.request.json.get('smtp_username'),
            password=bottle.request.json.get('smtp_password')
        )

        if is_success:
            firma.settings.smtp_active = True
            firma.settings.smtp_host = bottle.request.json.get('smtp_host')
            firma.settings.smtp_port = bottle.request.json.get('smtp_port')
            firma.settings.smtp_mail = bottle.request.json.get('smtp_mail')
            firma.settings.smtp_username = bottle.request.json.get('smtp_username')
            firma.settings.smtp_password = bottle.request.json.get('smtp_password')
            db.session.add(firma.settings)
            db.session.commit()

            return ({
                'is_success': True,
                'message': 'Podešavanja su sačuvana'
            })

        return ({
            'is_success': False,
            'message': 'Podešavanja nisu sačuvana. Veza sa SMTP host-om se ne može ostvariti.'
        })
    else:
        firma.settings.smtp_active = is_smtp_active
        firma.settings.smtp_host = None
        firma.settings.smtp_port = None
        firma.settings.smtp_mail = None
        firma.settings.smtp_username = None
        firma.settings.smtp_password = None
        db.session.add(firma.settings)
        db.session.commit()

        return ({
            'is_success': True,
            'message': 'Podešavanja su sačuvana.'
        })
