from typing import List
from typing import Optional

from sqlalchemy import sql

from backend.db import db
from backend.models import Firma, CompanySettings, JedinicaMjere
from backend.models import Komitent
from backend.models import NaplatniUredjaj
from backend.models import OrganizacionaJedinica

DEFAULT_MEASUREMENT_UNITS = [
    {'short_name': 'kom', 'name': 'komad', 'ui_default': 1},
    {'short_name': 'l', 'name': 'litar', 'ui_default': 0},
    {'short_name': 'kg', 'name': 'kilogram', 'ui_default': 0},
    {'short_name': 'm', 'name': 'metar', 'ui_default': 0},
    {'short_name': 'm2', 'name': 'kvadratni metar', 'ui_default': 0},
    {'short_name': 'm3', 'name': 'kubni metar', 'ui_default': 0},
    {'short_name': 'g', 'name': 'gram', 'ui_default': 0},
    {'short_name': 't', 'name': 'tona', 'ui_default': 0},
    {'short_name': 'par', 'name': 'par', 'ui_default': 0},
    {'short_name': 'k', 'name': 'karat', 'ui_default': 0},
    {'short_name': 'd', 'name': 'dan', 'ui_default': 0},
]


def get_filtered_companies(filters):
    query = db.session.query(Firma)

    if 'query' in filters and len(filters['query']) > 0:
        query = query.filter(sql.or_(
            Firma.naziv.contains(filters['query']),
            Firma.pib.like(filters['query'])
        ))

    return query


def update_is_active_by_id(company_id: int, is_active: bool):
    db.session.query(Firma).filter(Firma.id == company_id).update({
        Firma.je_aktivna: is_active
    })
    db.session.commit()


def update_taxpayer_status_by_id(company_id: int, is_taxpayer: bool):
    db.session.query(Firma).filter(Firma.id == company_id).update({
        Firma.je_poreski_obaveznik: is_taxpayer
    })
    db.session.commit()


def get_company_by_id(company_id: int) -> Optional[Firma]:
    return db.session.query(Firma) \
        .filter(Firma.id == company_id) \
        .first()


def listaj_po_pibu(pib: str) -> Optional[Firma]:
    return db.session.query(Firma) \
        .filter(Firma.pib == pib) \
        .first()


def listaj_naplatni_uredjaj_po_efi_kodu(efi_kod):
    return db.session.query(NaplatniUredjaj) \
        .filter(NaplatniUredjaj.efi_kod == efi_kod) \
        .first()


def get_buyer_by_id(buyer_id: int) -> Optional[Komitent]:
    if buyer_id is None:
        return None

    return db.session.query(Komitent) \
        .filter(Komitent.id == buyer_id) \
        .first()


def update_company_logo(firma_id, filepath, filename):
    db.session.query(Firma).filter(Firma.id == firma_id).update({
        'logo_filepath': filepath,
        'logo_filename': filename
    })

    db.session.commit()


def update_company_data(firma_id, data):
    result = db.session.query(Firma).filter(Firma.id == firma_id).update({
        'naziv': data['naziv'],
        'adresa': data['adresa'],
        'grad': data['grad'],
        'drzava': data['drzava'],
        'telefon': data['telefon'],
        'email': data['email'],
        'ziroracun': data['ziroracun'],
        'pdvbroj': data['pdvbroj']
    })

    db.session.commit()

    return result


def insert_company(data: dict):
    company = Firma()
    company.naziv = data['naziv']
    company.pib = data['pib']
    company.pdvbroj = data['pdvbroj']
    company.adresa = data['adresa']
    company.grad = data['grad']
    company.drzava = data['drzava']
    company.telefon = data['telefon']
    company.email = data['email']
    company.ziroracun = data['ziroracun']
    company.je_poreski_obaveznik = data['je_poreski_obaveznik']
    company.je_aktivna = True

    company.settings = CompanySettings()
    company.settings.smtp_active = False
    company.settings.smtp_host = None
    company.settings.smtp_port = None
    company.settings.smtp_mail = None
    company.settings.smtp_username = None
    company.settings.smtp_password = None
    company.settings.can_schedule = False

    for measurement_unit_dict in DEFAULT_MEASUREMENT_UNITS:
        measurement_unit = JedinicaMjere()
        measurement_unit.naziv = measurement_unit_dict['short_name']
        measurement_unit.opis = measurement_unit_dict['name']
        measurement_unit.ui_default = measurement_unit_dict['ui_default']
        measurement_unit.firma = company
        db.session.add(measurement_unit)

    db.session.add(company)
    db.session.commit()


def update_company_by_id(company_id, data):
    db.session.query(Firma).filter(Firma.id == company_id).update({
        Firma.naziv: data['naziv'],
        Firma.pib: data['pib'],
        Firma.pdvbroj: data['pdvbroj'],
        Firma.adresa: data['adresa'],
        Firma.grad: data['grad'],
        Firma.drzava: data['drzava'],
        Firma.telefon: data['telefon'],
        Firma.email: data['email'],
        Firma.ziroracun: data['ziroracun'],
        Firma.je_aktivna: data['je_aktivna'],
        Firma.je_poreski_obaveznik: data['je_poreski_obaveznik']
    })
    db.session.commit()


def get_business_units(customer_id: int) -> List[OrganizacionaJedinica]:
    return (
        db.session.query(OrganizacionaJedinica)
        .filter(OrganizacionaJedinica.firma_id == customer_id)
        .all()
    )
