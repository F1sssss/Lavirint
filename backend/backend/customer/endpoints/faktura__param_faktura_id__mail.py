from smtplib import SMTPException

import bottle
import simplejson as json

from backend.core import mailing
from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja


@requires_authentication
def api__faktura__param_faktura_id__mail(operater, firma, param_faktura_id):
    if not firma.settings.smtp_active:
        bottle.response.status = 400
        return bottle.response

    invoice = faktura_opb.listaj_fakturu_po_idu(param_faktura_id)

    if invoice.komitent.email is None or not mailing.is_valid_mail(invoice.komitent.email):
        return json.dumps({
            'is_success': False,
            'message': 'E-Mail nije ispravan'
        }, **podesavanja.JSON_DUMP_OPTIONS)

    try:
        mailing.send_invoice_mail(
            invoice,
            host=firma.settings.smtp_host,
            port=firma.settings.smtp_port,
            mail_from=firma.settings.smtp_mail,
            username=firma.settings.smtp_username,
            password=firma.settings.smtp_password,
            mail_to=invoice.komitent.email.strip()
        )

        return json.dumps({
            'is_success': True,
            'message': 'E-Mail je proslijeđen.'
        }, **podesavanja.JSON_DUMP_OPTIONS)
    except SMTPException:
        return json.dumps({
            'is_success': False,
            'message': 'Došlo je do greške u povezivanju sa mail serverom.'
        }, **podesavanja.JSON_DUMP_OPTIONS)
    except Exception:
        return json.dumps({
            'is_success': False,
            'message': 'Došlo je do nepoznate greške.'
        }, **podesavanja.JSON_DUMP_OPTIONS)