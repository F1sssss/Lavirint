from backend.db import db
from backend.models import VrstaPlacanja
from backend.opb.helpers import dohvati_stranicu


def test_payment_method_count():
    assert 16 == db.session.query(VrstaPlacanja).count()


def test_dohvati_stranicu():
    query = db.session.query(VrstaPlacanja)

    result = dohvati_stranicu(query, 2, 2)

    assert isinstance(result, dict)
    assert result['broj_stranice'] == 2
    assert result['broj_stavki_po_stranici'] == 2
    assert len(result['stavke']) == 2
