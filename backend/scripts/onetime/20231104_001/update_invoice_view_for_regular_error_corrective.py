import math

from backend.db import db
from backend.models import Faktura
from backend.opb.helpers import timing

total_rows = db.session.query(Faktura) \
    .filter(Faktura.tip_fakture_id.in_([Faktura.TYPE_ERROR_CORRECTIVE])) \
    .count()

batch_size = 1000
total_batches = math.ceil(total_rows / batch_size)

for ii in range(0, total_batches):
    with timing():
        print(
            f'{ii + 1}/{total_batches}',
            ii * batch_size,  # offset
            ii * batch_size + batch_size,
            total_rows,
            total_rows - ii * batch_size,
            end=''
        )
        subquery = db.session.query(Faktura.id) \
            .filter(Faktura.tip_fakture_id.in_([Faktura.TYPE_ERROR_CORRECTIVE])) \
            .limit(batch_size) \
            .offset(ii * batch_size) \
            .all()

        for row in subquery:
            invoice = db.session.query(Faktura) \
                .filter(Faktura.id == row.id) \
                .first()

            invoice.customer_invoice_view = invoice.korigovana_faktura.customer_invoice_view

        db.session.commit()
