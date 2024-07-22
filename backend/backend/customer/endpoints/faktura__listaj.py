import bottle
import simplejson as json

from backend import enums
from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.opb.helpers import InvoiceFilterData
from backend.opb.helpers import dohvati_stranicu
from backend.podesavanja import podesavanja
from backend.serializers import faktura_schema


@requires_authentication
def api__faktura__listaj(operater, firma):
    filter_data = InvoiceFilterData.load_from_form_dict(bottle.request.query)

    query = faktura_opb.get_invoice_filter_query(firma.id, operater.naplatni_uredjaj_id, filter_data, enums.CustomerInvoiceView.REGULAR_INVOICES)

    rezultat = dohvati_stranicu(query, filter_data.broj_stranice, filter_data.broj_stavki_po_stranici)

    rezultat['stavke'] = faktura_schema.dump(rezultat['stavke'], many=True)

    return json.dumps(rezultat, **podesavanja.JSON_DUMP_OPTIONS)
