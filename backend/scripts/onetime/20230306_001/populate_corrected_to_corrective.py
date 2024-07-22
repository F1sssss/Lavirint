import json

from backend import models as m
from backend.db import db

data = []

cancellations = db.session.query(m.Faktura).filter(m.Faktura.tip_fakture_id == m.Faktura.TYPE_CANCELLATION).all()
for cancellation in cancellations:
    data.append({
        'corrected_invoice_id': cancellation.storno_faktura_id,
        'corrective_invoice_id': cancellation.id
    })

corrections = db.session.query(m.VezaKorektivnaFaktura).all()
for correction in corrections:
    corrective_invoice = db.session.query(m.Faktura).get(correction.korektivna_faktura_id)

    data.append({
        'corrected_invoice_id': correction.korigovana_faktura_id,
        'corrective_invoice_id': corrective_invoice.id
    })


data = sorted(data, key=lambda t: t['corrective_invoice_id'])

for row in data:
    insert = m.CorrectedToCorrective.insert().values(
        corrected_invoice_id=row['corrected_invoice_id'],
        corrective_invoice_id=row['corrective_invoice_id']
    )
    db.engine.execute(insert)
