import bottle
import simplejson as json

from backend.customer import parsing
from backend.customer.auth import requires_authentication
from backend.logging import logger
from backend.models import Faktura
from backend.models import Operater
from backend.opb import credit_note_opb
from backend.opb import faktura_opb
from backend.opb import komitent_opb
from backend.opb import misc_opb
from backend.podesavanja import podesavanja


@requires_authentication
def views__faktura_slobodan_unos_korekcije__fiskalizuj(operater, firma):
    error_message, post_data = validate_post_data(bottle.request.json, operater)
    if error_message is not None:
        logger.error(error_message)
        bottle.response.status = 400
        return bottle.response

    post_data['operater'] = operater
    post_data['operater_id'] = operater.id

    post_data['firma'] = firma
    post_data['firma_id'] = firma.id

    post_data['naplatni_uredjaj'] = operater.naplatni_uredjaj
    post_data['naplatni_uredjaj_id'] = operater.naplatni_uredjaj.id

    invoice = faktura_opb.make_corrective_invoice_from_dict(post_data, operater.naplatni_uredjaj)

    return json.dumps(
        serialize_response(invoice),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def validate_post_data(data: dict, operater: Operater):
    try:
        r = data.copy()

        r['is_cash'] = parsing.get_bool(data, 'is_cash')

        corrected_invoice_reference = parsing.get_dict(data, 'correctedInvoiceReference')
        ref_type = parsing.get_string(corrected_invoice_reference, 'type')
        if ref_type == 'invoice':
            r['corrected_invoice_reference'] = {}
            r['corrected_invoice_reference']['type'] = 'invoice'
            r['corrected_invoice_reference']['invoice_id'] = invoice_id = parsing.get_int(corrected_invoice_reference, 'invoiceId')
            r['corrected_invoice_reference']['invoice'] = invoice = faktura_opb.listaj_fakturu_po_idu(invoice_id)
            if invoice is None:
                raise parsing.ParsingError(f'Invoice #{invoice_id} does not exist.')
            if operater.firma.id != invoice.id:
                raise parsing.ParsingError(f'Invoice #{invoice_id} does not exist.')
        elif ref_type == 'credit_note':
            r['corrected_invoice_reference'] = {}
            r['corrected_invoice_reference']['type'] = 'credit_note'
            r['corrected_invoice_reference']['credit_note_id'] = credit_note_id = parsing.get_int(corrected_invoice_reference, 'creditNoteId')
            r['corrected_invoice_reference']['credit_note'] = credit_note = credit_note_opb.get_credit_note_by_id(credit_note_id)
            if credit_note is None:
                raise parsing.ParsingError(f'Credit note #{credit_note_id} does not exist.')
            if credit_note.firma.id != operater.firma_id:
                raise parsing.ParsingError(f'Credit note #{credit_note_id} does not exist.')
        else:
            raise parsing.ParsingError(f'Parameter "type" value must be "invoice" or "credit_note"')

        del data['correctedInvoiceReference']

        r['datumvalute'] = parsing.get_datetime(data, 'datumvalute')
        r['poreski_period'] = parsing.get_tax_period(data, 'poreski_period')
        r['datum_prometa'] = parsing.get_datetime(data, 'datum_prometa', optional=True)
        r['tip_fakture_id'] = Faktura.TYPE_CORRECTIVE
        r['komitent_id'] = buyer_id = parsing.get_int(data, 'komitent_id', optional=True)
        if buyer_id is not None:
            r['komitent'] = komitent = komitent_opb.get_by_id(buyer_id)
            if komitent is None:
                raise parsing.ParsingError(f'Buyer #{buyer_id} does not exist.')
            if komitent.pibvlasnikapodatka != operater.firma.pib:
                raise parsing.ParsingError(f'Buyer #{buyer_id} does not exist.')

        r['valuta_id'] = currency_id = parsing.get_int(data, 'valuta_id')
        r['valuta'] = currency = misc_opb.get_currency_by_id(currency_id)
        if currency is None:
            raise parsing.ParsingError(f'Currency #{currency_id} does not exist.')

        if not r['is_cash'] and r['komitent'] is None:
            return 'Kupac mora biti definisan kod bezgotovinskih računa.', None

        return None, r
    except parsing.ParsingError as error:
        return str(error), None
    except (Exception, ):
        logger.exception("Došlo je do nepredviđene greške.")
        return 'Došlo je do nepredviđene greške.', None


def serialize_response(invoice: Faktura):
    pass
