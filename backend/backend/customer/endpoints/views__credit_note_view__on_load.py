import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.models import KnjiznoOdobrenje, Faktura
from backend.opb import credit_note_opb
from backend.opb.helpers import dohvati_stranicu
from backend.podesavanja import podesavanja


@requires_authentication
def views__credit_note_view__on_load(operater, firma):
    broj_stranice = int(bottle.request.json.get('broj_stranice', 1))
    broj_stavki_po_stranici = int(bottle.request.json.get('broj_stavki_po_stranici', 12))

    stranica = credit_note_opb.get_customer_view_items(
        operater.naplatni_uredjaj_id,
        page_number=broj_stranice,
        items_per_page=broj_stavki_po_stranici
    )

    return json.dumps(
        serialize_response(stranica),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def serialize_response(data):
    serialized_items = []
    for item in data['stavke']:
        if isinstance(item, KnjiznoOdobrenje):
            serialized_credit_note = {
                'id': item.id,
                'type': 'credit_note',
                'efi_ordinal_number': item.efi_ordinal_number,
                'discount_amount_with_tax': item.discount_amount_with_tax,
                'return_amount_with_tax': item.return_amount_with_tax,
                'return_and_discount_amount_with_tax': item.return_and_discount_amount_with_tax,
                'datum_fiskalizacije': item.datum_fiskalizacije.isoformat(),
                'efi_broj_fakture': item.efi_broj_fakture,
                'efi_verify_url': item.efi_verify_url,
                'fakture': [],
                'komitent_id': item.komitent_id,
                'komitent': {
                    'id': item.komitent.id,
                    'naziv': item.komitent.naziv,
                }
            }

            for invoice in item.fakture:
                serialized_credit_note['fakture'].append({
                    'id': invoice.id,
                    'efi_ordinal_number': invoice.efi_ordinal_number,
                    'datumfakture': invoice.datumfakture.isoformat(),
                    'ukupna_cijena_prodajna': invoice.ukupna_cijena_prodajna
                })

            serialized_iic_refs = []
            for iic_ref in item.iic_refs:
                serialized_iic_refs.append({
                    'iic': iic_ref.iic,
                    'invoice_id': iic_ref.invoice_id,
                    'issue_datetime': iic_ref.issue_datetime.isoformat(),
                    'amount': iic_ref.amount_21 + iic_ref.amount_7 + iic_ref.amount_0 + iic_ref.amount_exempt,
                    'verification_url': iic_ref.verification_url
                })
            serialized_credit_note['iic_refs'] = serialized_iic_refs

            serialized_items.append(serialized_credit_note)

        if isinstance(item, Faktura):
            serialized_invoice = {
                'id': item.id,
                'type': 'invoice',
                'efi_ordinal_number': item.efi_ordinal_number,
                'tip_fakture_id': item.tip_fakture_id,
                'datumfakture': item.datumfakture.isoformat(),
                'efi_broj_fakture': item.efi_broj_fakture,
                'efi_verify_url': item.efi_verify_url,
                'valuta_id': item.valuta_id,
                'valuta': {
                    'id': item.valuta.id,
                    'naziv_me': item.valuta.naziv_me,
                    'iso_4217_alfanumericki_kod': item.valuta.iso_4217_alfanumericki_kod
                },
                'ukupna_cijena_prodajna': item.ukupna_cijena_prodajna,
                'porez_iznos': item.porez_iznos,
                'ukupna_cijena_rabatisana': item.ukupna_cijena_rabatisana,
                'ukupna_cijena_puna': item.ukupna_cijena_puna,
                'poreski_period': item.poreski_period.isoformat(),
                'komitent_id': None,
                'komitent': {},
                'payment_methods': []
            }

            if item.komitent_id is not None:
                serialized_invoice['komitent_id'] = item.komitent_id
                serialized_invoice['komitent'] = {
                    'id': item.komitent.id,
                    'naziv': item.komitent.naziv
                }

            for payment_method in item.payment_methods:
                serialized_invoice['payment_methods'].append({
                    'payment_method_type': {
                        'id': payment_method.payment_method_type.id,
                        'description': payment_method.payment_method_type.description
                    },
                    'amount': payment_method.amount
                })

            serialized_items.append(serialized_invoice)

    return {
        'stranica': {
            'broj_stranice': data['broj_stranice'],
            'broj_stavki_po_stranici': data['broj_stavki_po_stranici'],
            'ukupan_broj_stavki': data['ukupan_broj_stavki'],
            'stavke': serialized_items
        }
    }
