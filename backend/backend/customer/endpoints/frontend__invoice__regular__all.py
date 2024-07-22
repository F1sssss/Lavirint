import bottle
import simplejson as json

from backend import enums
from backend.customer.auth import requires_authentication
from backend.db import db
from backend.models import PaymentMethodType
from backend.opb import faktura_opb
from backend.opb import komitent_opb
from backend.opb.helpers import InvoiceFilterData
from backend.opb.helpers import dohvati_stranicu
from backend.podesavanja import podesavanja
from backend.serializers import invoice_view_schema
from backend.serializers import komitent_schema
from backend.serializers import payment_method_type_schema


@requires_authentication
def api__frontend__invoice__regular__all(operater, firma):
    base_filter = InvoiceFilterData()
    total_items = faktura_opb.get_invoice_filter_query(firma.id, operater.naplatni_uredjaj_id, base_filter, enums.CustomerInvoiceView.REGULAR_INVOICES).count()

    invoice_filters = InvoiceFilterData.load_from_form_dict(bottle.request.query)
    query = faktura_opb.get_invoice_filter_query(firma.id, operater.naplatni_uredjaj_id, invoice_filters, enums.CustomerInvoiceView.REGULAR_INVOICES)
    stranica = dohvati_stranicu(query, invoice_filters.broj_stranice, invoice_filters.broj_stavki_po_stranici)

    stranica['stavke'] = invoice_view_schema.dump(stranica['stavke'], many=True)
    stranica['total_items'] = total_items
    komitenti = komitent_opb.komitent_po_pibu_query(firma.pib).all()

    payment_method_types = db.session.query(PaymentMethodType) \
        .filter(PaymentMethodType.is_active.is_(True)) \
        .order_by(PaymentMethodType.sort_weight) \
        .all()

    return json.dumps({
        'komitenti': komitent_schema.dump(komitenti, many=True),
        'stranica': stranica,
        'payment_method_types': payment_method_type_schema.dump(payment_method_types, many=True)
    }, **podesavanja.JSON_DUMP_OPTIONS)
