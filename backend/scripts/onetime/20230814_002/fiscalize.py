from datetime import datetime

import pytz

from backend import models
from backend.db import db
from backend.opb.faktura_opb import InvoiceProcessing
from backend.opb.faktura_opb import fiscalize_invoice
from backend.opb.faktura_opb import save_invoice_print
from backend.opb.faktura_opb import update_stock_from_invoice

processing = InvoiceProcessing()
invoice = db.session.query(models.Faktura).get(3433406)

fiscalization_date = datetime.now(pytz.timezone('Europe/Podgorica'))
with processing.acquire_lock(invoice.naplatni_uredjaj.id) as _:
    invoice = fiscalize_invoice(invoice, fiscalization_date)
    update_stock_from_invoice(invoice)
    save_invoice_print(invoice)

print(processing.get_message())
print(invoice)
