from typing import Union, Optional

from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy import sql

from backend.db import db
from backend.models import Firma
from backend.models import Operater


def get_operator_by_id(operater_id: int) -> Union[Operater, None]:
    return db.session.query(Operater) \
        .filter(Operater.id == operater_id) \
        .first()


def nadji_operatera_po_pibu_i_mejlu(pib: str, email: str) -> Union[Operater, None]:
    return db.session.query(Operater) \
        .filter(Operater.email == email) \
        .filter(Operater.firma.has(Firma.pib == pib)) \
        .filter(Operater.aktivan == 1) \
        .first()


def provjeri_operatera(operater: Operater, lozinka: str) -> bool:
    return pbkdf2_sha256.verify(lozinka, operater.lozinka)


def operater_izmijeni(operater_id: int, podaci: dict) -> None:
    db.session.query(Operater).filter(Operater.id == operater_id).update({
        'lozinka': pbkdf2_sha256.hash(podaci['lozinka'])
    })

    db.session.commit()


def get_customer_user_by_efi_code(company_id: int, efi_code: str) -> Optional[Operater]:
    return db.session.query(Operater) \
        .filter(Operater.firma_id == company_id) \
        .filter(Operater.kodoperatera == efi_code) \
        .first()


def get_customer_users(search_query: str):
    query = db.session.query(Operater)
    if search_query is not None:
        query = db.session.query(Operater).filter(sql.or_(
            Operater.email.contains(search_query),
            Operater.ime.contains(search_query),
            Operater.kodoperatera.contains(search_query),
            Operater.firma.has(Firma.naziv.contains(search_query)),
            Operater.firma.has(Firma.pib.like(search_query))
        ))

    return query
