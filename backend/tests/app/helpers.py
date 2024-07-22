from backend import models
from backend.opb.faktura_opb import get_tax_groups_from_items


def test_get_tax_groups_1():
    invoice = models.Faktura()
    invoice.stavke.append(models.FakturaStavka())
    invoice.ukupna_cijena_osnovna = 1
    invoice.ukupna_cijena_rabatisana = 1
    invoice.ukupna_cijena_prodajna = 1.21
    invoice.ukupna_cijena_puna = 1.21
    invoice.porez_procenat = 21
    invoice.porez_iznos = 0.21
    invoice.rabat_procenat = 0
    invoice.rabat_iznos_osnovni = 0
    invoice.rabat_iznos_prodajni = 0
    invoice.credit_note_turnover_remaining = 1.21
    invoice.credit_note_turnover_used = 0

    tax_groups = get_tax_groups_from_items(invoice)

    assert isinstance(tax_groups[0], models.FakturaGrupaPoreza)
    assert tax_groups[0].ukupna_cijena_osnovna == 1
    assert tax_groups[0].ukupna_cijena_rabatisana == 1
    assert tax_groups[0].ukupna_cijena_prodajna == 1.21
    assert tax_groups[0].ukupna_cijena_puna == 1.21
    assert tax_groups[0].porez_procenat == 21
    assert tax_groups[0].porez_iznos == 0.21
    assert tax_groups[0].rabat_procenat == 0
    assert tax_groups[0].rabat_iznos_osnovni == 0
    assert tax_groups[0].rabat_iznos_prodajni == 0
    assert tax_groups[0].credit_note_turnover_remaining == 1.21
    assert tax_groups[0].credit_note_turnover_used == 0
