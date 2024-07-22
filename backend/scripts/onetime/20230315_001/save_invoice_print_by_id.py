import sys

from backend import models as m
from backend.db import db
from backend.opb import faktura_opb

invoice = db.session.query(m.Faktura).get(sys.argv[1])
faktura_opb.save_invoice_print(invoice)
