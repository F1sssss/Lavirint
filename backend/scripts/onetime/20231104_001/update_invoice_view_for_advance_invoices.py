import math
from contextlib import contextmanager

from sqlalchemy import and_

from backend import enums
from backend.db import db
from backend.models import Faktura
from backend.opb.helpers import generate_batch
from backend.opb.helpers import timing

total_rows = db.session.query(Faktura) \
    .filter(Faktura.tip_fakture_id == Faktura.TYPE_ADVANCE) \
    .count()
batch_size = 1000
total_batches = math.ceil(total_rows / batch_size)

for ii in range(0, total_batches):
    with timing():
        print(
            f'{ii+1}/{total_batches}',
            ii * batch_size,  # offset
            ii * batch_size + batch_size,
            total_rows,
            total_rows - ii * batch_size,
            end=''
        )
        subquery = db.session.query(Faktura.id) \
            .filter(Faktura.tip_fakture_id == Faktura.TYPE_ADVANCE) \
            .limit(batch_size) \
            .offset(ii * batch_size) \
            .all()

        ids = [row.id for row in subquery]

        db.session.query(Faktura) \
            .filter(Faktura.id.in_(ids)) \
            .update({Faktura.customer_invoice_view: enums.CustomerInvoiceView.ADVANCE_INVOICES.value})

        db.session.commit()
