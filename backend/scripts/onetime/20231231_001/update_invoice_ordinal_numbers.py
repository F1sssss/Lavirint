import math

from sqlalchemy import sql, func

from backend import enums
from backend.db import db
from backend.models import Faktura
from backend.opb.helpers import timing

total_rows = db.session.query(func.max(Faktura.id)) \
    .scalar()

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
            .limit(batch_size) \
            .offset(ii * batch_size) \
            .all()

        ids = [row.id for row in subquery]

        db.session.query(Faktura) \
            .filter(Faktura.id.in_(ids)) \
            .update({
                Faktura.efi_ordinal_number: sql.text('redni_broj_fakture'),
                Faktura.internal_ordinal_number: sql.text('redni_broj_fakture')
            })

        db.session.commit()