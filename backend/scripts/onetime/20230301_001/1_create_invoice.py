from datetime import datetime
from uuid import uuid4

from _decimal import Decimal

from backend import models as m
from backend.db import db
from backend.opb import faktura_opb
from backend.opb.faktura_opb import fiscalize_invoice

now = datetime.now()

# ----------------------------------------------------------------------------------------------------------------------
invoice = m.Faktura()
invoice.uuid = uuid4()
invoice.redni_broj_fakture = None
invoice.datumfakture = None
invoice.datumvalute = now
invoice.datum_prometa = now
invoice.poreski_period = now.replace(hour=0, minute=0, second=0, microsecond=0)
invoice.status = 1
invoice.napomena = None

invoice.vrstaplacanja_id = None  # Deprecated
invoice.vrstaplacanja = None  # Deprecated

invoice.is_cash = False

invoice.operater = db.session.query(m.Operater).get(388)
invoice.brojoperatera = invoice.operater.id  # id=388

invoice.komitent = db.session.query(m.Komitent).get(599)  # IRIS LEATHER DOO
invoice.komitent_id = invoice.komitent.id

invoice.firma = db.session.query(m.Firma).get(241)  # DIGITAL ME DOO
invoice.firma_id = invoice.firma.id

invoice.naplatni_uredjaj = db.session.query(m.NaplatniUredjaj).get(252)
invoice.naplatni_uredjaj_id = invoice.naplatni_uredjaj.id

invoice.valuta = db.session.query(m.Valuta).get(50)  # EUR
invoice.valuta_id = invoice.valuta.id
invoice.kurs_razmjene = 1

invoice.tip_fakture = db.session.query(m.FakturaTip).get(m.Faktura.TYPE_REGULAR)
invoice.tip_fakture_id = invoice.tip_fakture.id

invoice.lokacija_dokumenta = None

# ----------------------------------------------------------------------------------------------------------------------

invoice_item_1 = m.FakturaStavka()
invoice_item_1.faktura_id = None
invoice_item_1.sifra = None
invoice_item_1.naziv = 'Test stavka 1'

invoice_item_1.jedinica_mjere = db.session.query(m.JedinicaMjere).get(2431)  # Komad
invoice_item_1.jedinica_mjere_id = invoice_item_1.jedinica_mjere.id

faktura_opb.update_invoice_item_from_upb(
    item=invoice_item_1,
    quantity=Decimal(1),
    price=Decimal(1),
    tax_percentage=Decimal(21),
    rebate_percentage=Decimal(0)
)

invoice.stavke.append(invoice_item_1)

# ----------------------------------------------------------------------------------------------------------------------

invoice_item_2 = m.FakturaStavka()
invoice_item_2.faktura_id = None
invoice_item_2.sifra = None
invoice_item_2.naziv = 'Test stavka 2'

invoice_item_2.jedinica_mjere = db.session.query(m.JedinicaMjere).get(2431)  # Komad
invoice_item_2.jedinica_mjere_id = invoice_item_2.jedinica_mjere.id

faktura_opb.update_invoice_item_from_upb(
    item=invoice_item_2,
    quantity=Decimal(1),
    price=Decimal(1),
    tax_percentage=Decimal(21),
    rebate_percentage=Decimal(0)
)

invoice.stavke.append(invoice_item_2)

# ----------------------------------------------------------------------------------------------------------------------

for grupa_poreza in faktura_opb.get_tax_groups_from_items(invoice):
    invoice.grupe_poreza.append(grupa_poreza)

# ----------------------------------------------------------------------------------------------------------------------

faktura_opb.update_invoice_totals_from_items(invoice, invoice.stavke)
invoice.credit_note_turnover_used = Decimal(0)
invoice.credit_note_turnover_remaining = invoice.ukupna_cijena_prodajna

invoice.korigovana_ukupna_cijena_osnovna = invoice.ukupna_cijena_osnovna
invoice.korigovana_ukupna_cijena_rabatisana = invoice.ukupna_cijena_rabatisana
invoice.korigovana_ukupna_cijena_puna = invoice.ukupna_cijena_puna
invoice.korigovana_ukupna_cijena_prodajna = invoice.ukupna_cijena_prodajna
invoice.korigovani_porez_iznos = invoice.porez_iznos
invoice.korigovani_rabat_iznos_osnovni = invoice.rabat_iznos_osnovni
invoice.korigovani_rabat_iznos_prodajni = invoice.rabat_iznos_prodajni
invoice.corrected_tax_exemption_amount = invoice.tax_exemption_amount

# ----------------------------------------------------------------------------------------------------------------------

payment_method_1 = m.PaymentMethod()
payment_method_1.invoice_id = None
payment_method_1.advance_invoice_id = None
payment_method_1.advance_invoice = None
payment_method_1.payment_method_type = db.session.query(m.PaymentMethodType).get(m.PaymentMethod.TYPE_ACCOUNT)
payment_method_1.payment_method_type_id = payment_method_1.payment_method_type.id
payment_method_1.amount = invoice.ukupna_cijena_prodajna
invoice.payment_methods.append(payment_method_1)

# ----------------------------------------------------------------------------------------------------------------------

db.session.add(invoice)
db.session.commit()

fiscalize_invoice(invoice, now)