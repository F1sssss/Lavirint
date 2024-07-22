import math

from sqlalchemy import sql, func

from backend.db import db
from backend.models import KnjiznoOdobrenje
from backend.opb.helpers import timing

total_rows = db.session.query(func.max(KnjiznoOdobrenje.id)) \
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
        subquery = db.session.query(KnjiznoOdobrenje.id) \
            .limit(batch_size) \
            .offset(ii * batch_size) \
            .all()

        ids = [row.id for row in subquery]

        db.session.query(KnjiznoOdobrenje) \
            .filter(KnjiznoOdobrenje.id.in_(ids)) \
            .update({
                KnjiznoOdobrenje.efi_ordinal_number: sql.text('redni_broj'),
                KnjiznoOdobrenje.internal_ordinal_number: sql.text('redni_broj')
            })

        db.session.commit()
