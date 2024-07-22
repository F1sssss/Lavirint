from backend import models as m
from backend.db import db

db.session.query(m.FakturaStavka).update({
    'korigovana_jedinicna_cijena_osnovna': m.FakturaStavka.jedinicna_cijena_osnovna,
    'korigovana_jedinicna_cijena_rabatisana': m.FakturaStavka.jedinicna_cijena_rabatisana,
    'korigovana_jedinicna_cijena_puna': m.FakturaStavka.jedinicna_cijena_puna,
    'korigovana_jedinicna_cijena_prodajna': m.FakturaStavka.jedinicna_cijena_prodajna,
})
db.session.commit()
