from backend import models as m
from backend.db import db

counter = 0

corrections = db.session.query(m.CorrectedToCorrective).all()
corrections_length = len(corrections)

for ii, correction in enumerate(corrections):
    counter += 1
    # print('%s/%s' % (ii + 1, corrections_length))
    korigovana_faktura = db.session.query(m.Faktura).get(correction.corrected_invoice_id)
    korektivna_faktura = db.session.query(m.Faktura).get(correction.corrective_invoice_id)

    if len(korigovana_faktura.stavke) != len(korektivna_faktura.stavke):
        print('Must be handled manually\n'
              f'Corrective invoice {korektivna_faktura.id}\n'
              f'Corrected invoice {korigovana_faktura.id}\n')
        continue

    for jj, korigovana_stavka in enumerate(korigovana_faktura.stavke):
        if korektivna_faktura.stavke[jj].naziv != korigovana_stavka.naziv:
            print('Must be handled manually\n'
                  f'Corrective invoice {korektivna_faktura.id}\n'
                  f'Corrected invoice {korigovana_faktura.id}\n')
            break

        db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == korektivna_faktura.stavke[jj].id).update({
            'corrected_invoice_item_id': korigovana_stavka.id
        })
        db.session.commit()
    else:
        continue

db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 649924).update({'corrected_invoice_item_id': 639146})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 649925).update({'corrected_invoice_item_id': 639146})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 649926).update({'corrected_invoice_item_id': 639147})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 649927).update({'corrected_invoice_item_id': 639147})

db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 659493).update({'corrected_invoice_item_id': 659247})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 659494).update({'corrected_invoice_item_id': 659247})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 659495).update({'corrected_invoice_item_id': 659248})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 659496).update({'corrected_invoice_item_id': 659248})

db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 663429).update({'corrected_invoice_item_id': 291140})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 663430).update({'corrected_invoice_item_id': 291140})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 663431).update({'corrected_invoice_item_id': 291140})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 663432).update({'corrected_invoice_item_id': 291141})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 663433).update({'corrected_invoice_item_id': 291141})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 663434).update({'corrected_invoice_item_id': 291141})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 663435).update({'corrected_invoice_item_id': 291142})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 663436).update({'corrected_invoice_item_id': 291142})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 663437).update({'corrected_invoice_item_id': 291142})

db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 1118938).update({'corrected_invoice_item_id': 1115707})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 1118939).update({'corrected_invoice_item_id': 1115708})
db.session.query(m.FakturaStavka).filter(m.FakturaStavka.id == 1118940).update({'corrected_invoice_item_id': 1115709})
db.session.commit()
