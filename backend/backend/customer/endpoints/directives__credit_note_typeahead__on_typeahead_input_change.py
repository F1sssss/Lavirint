from typing import List

import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.logging import logger
from backend.models import KnjiznoOdobrenje
from backend.opb import credit_note_opb
from backend.podesavanja import podesavanja


@requires_authentication
def directives__credit_note_typeahead__on_typeahead_input_change(operater, firma):
    error_message, post_data = validate_post_data(bottle.request.json)
    if error_message is not None:
        logger.error(error_message)
        bottle.response.status = 400
        return bottle.response

    credit_notes = credit_note_opb.get_credit_notes_by_payment_device_id(operater.naplatni_uredjaj_id)

    return json.dumps(
        serialize_response(credit_notes),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def validate_post_data(data):
    post_data = {}
    post_data['query'] = data.get('query', '')

    if not isinstance(post_data['query'], str):
        return 'Parameter "query" must be string'

    return None, post_data


def serialize_response(credit_notes: List[KnjiznoOdobrenje]):
    serialized_credit_notes = []
    for credit_note in credit_notes:
        serialized_credit_notes.append({
            'id': credit_note.id,
            'fiscalizationDate': credit_note.datum_fiskalizacije.isoformat(),
            'ordinalNumber': '%s/%s' % (credit_note.efi_ordinal_number, credit_note.datum_fiskalizacije.year),
            'returnAmountWithTax': credit_note.return_amount_with_tax,
            'returnAmount': credit_note.return_amount,
            'discountAmountWithTax': credit_note.discount_amount_with_tax,
            'discountAmount': credit_note.discount_amount,
            'returnAndDiscountAmountWithTax': credit_note.return_and_discount_amount_with_tax,
            'returnAndDiscountAmount': credit_note.return_and_discount_amount,
            'currency': {
                'id': credit_note.valuta.id,
                'isoCode': credit_note.valuta.iso_4217_alfanumericki_kod,
                'name': credit_note.valuta.naziv_me
            },
            'buyer': {
                'id': credit_note.komitent.id,
                'name': credit_note.komitent.naziv,
                'address': credit_note.komitent.adresa,
                'city': credit_note.komitent.grad,
                'country': {
                    'id': credit_note.komitent.drzave.id,
                    'name': credit_note.komitent.drzave.drzava
                },
                'identificationType': {
                    'id': credit_note.komitent.tip_identifikacione_oznake.id,
                    'description': credit_note.komitent.tip_identifikacione_oznake.naziv
                },
                'identificationNumber': credit_note.komitent.identifikaciona_oznaka
            }
        })

    return {
        'creditNotes': serialized_credit_notes
    }
