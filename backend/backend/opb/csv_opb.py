from backend.db import db
from backend.models import CsvObrada
from backend.models import CsvObradaOvlascenje
from backend.models import Firma


def listaj_obradu_po_idu(obrada_id):
    return db.session.query(CsvObrada).get(obrada_id)


def listaj_ovlascenje_po_pibu(obrada_id, firma_pib):
    return db.session.query(CsvObradaOvlascenje) \
        .filter(CsvObradaOvlascenje.csv_obrada_id == obrada_id) \
        .filter(CsvObradaOvlascenje.firma.has(Firma.pib == firma_pib)) \
        .first()
