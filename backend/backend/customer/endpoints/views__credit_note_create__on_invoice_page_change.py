import bottle
import simplejson as json

from backend import enums
from backend.customer.auth import requires_authentication
from backend.models import Faktura
from backend.opb import faktura_opb
from backend.opb.helpers import InvoiceFilterData
from backend.opb.helpers import dohvati_stranicu
from backend.podesavanja import podesavanja
from backend.serializers import invoice_search_result_schema


@requires_authentication
def views__credit_note_create__on_invoice_page_change(operater, firma):
    filter_data = InvoiceFilterData.load_from_dict(bottle.request.json)
    filter_data.invoice_type_ids = [Faktura.TYPE_REGULAR]
    query = faktura_opb.get_invoice_filter_query(firma.id, operater.naplatni_uredjaj_id, filter_data, enums.CustomerInvoiceView.REGULAR_INVOICES)
    invoice_page = dohvati_stranicu(query, filter_data.broj_stranice, filter_data.broj_stavki_po_stranici)
    return json.dumps({
        'stranica': invoice_search_result_schema.dump(invoice_page)
    }, **podesavanja.JSON_DUMP_OPTIONS)
