from typing import List

from backend.db import db
from backend.models import Artikal
from backend.models import Firma
from backend.models import GrupaArtikala
from backend.models import Magacin
from backend.models import MagacinZaliha


def artikal__listaj(firma_id):
    return db.session.query(Artikal) \
        .filter(Artikal.grupa_artikala.has(firma_id=firma_id)) \
        .filter(Artikal.is_deleted.is_not(True)) \
        .all()


def artikal__po_id__listaj(firma_id, artikal_id):
    return db.session.query(Artikal) \
        .filter(Artikal.grupa_artikala.has(firma_id=firma_id), Artikal.id == artikal_id) \
        .first()


def artikal__dodaj(magacin_id: int, podaci: dict, firma: Firma):
    artikal_data = podaci['artikal']
    artikal = Artikal()
    artikal.sifra = artikal_data.get('sifra')
    artikal.barkod = artikal_data.get('barkod')
    artikal.naziv = artikal_data['naziv']
    artikal.opis = artikal_data.get('opis')
    artikal.is_deleted = False
    artikal.grupa_artikala_id = artikal_data['grupa_artikala_id']
    artikal.jedinica_mjere_id = artikal_data['jedinica_mjere_id']
    db.session.add(artikal)

    zaliha_data = podaci['magacin_zaliha']
    magacini = db.session.query(Magacin).filter(Magacin.firma_id == firma.id).all()
    for magacin in magacini:
        zaliha = MagacinZaliha()
        zaliha.artikal = artikal
        zaliha.magacin = magacin
        zaliha.tax_exemption_reason_id = zaliha_data.get('tax_exemption_reason_id')
        zaliha.izvor_kalkulacije = zaliha_data['izvor_kalkulacije']
        zaliha.jedinicna_cijena_osnovna = zaliha_data['jedinicna_cijena_osnovna']
        zaliha.jedinicna_cijena_puna = zaliha_data['jedinicna_cijena_puna']
        zaliha.porez_procenat = zaliha_data['porez_procenat']
        zaliha.raspoloziva_kolicina = zaliha_data['raspoloziva_kolicina'] if magacin.id == magacin_id else 0

        db.session.add(zaliha)

    db.session.commit()

    return artikal


def artikal__po_id__izmijeni(
        magacin_id: int,
        artikal_id: int,
        podaci: dict, firma: Firma
):
    artikal = db.session.query(Artikal) \
        .filter(Artikal.id == artikal_id) \
        .filter(Artikal.grupa_artikala.has(firma_id=firma.id)) \
        .first()

    artikal_data = podaci['artikal']

    artikal.sifra = artikal_data.get('sifra')
    artikal.barkod = artikal_data.get('barkod')
    artikal.naziv = artikal_data['naziv']
    artikal.opis = artikal_data.get('opis')
    artikal.grupa_artikala_id = artikal_data['grupa_artikala_id']
    artikal.jedinica_mjere_id = artikal_data['jedinica_mjere_id']
    db.session.add(artikal)

    zaliha_data = podaci['magacin_zaliha']
    zaliha: MagacinZaliha = db.session.query(MagacinZaliha) \
        .filter(MagacinZaliha.artikal_id == artikal_id) \
        .first()
    zaliha.izvor_kalkulacije = zaliha_data['izvor_kalkulacije']
    zaliha.jedinicna_cijena_osnovna = zaliha_data['jedinicna_cijena_osnovna']
    zaliha.jedinicna_cijena_puna = zaliha_data['jedinicna_cijena_puna']
    zaliha.porez_procenat = zaliha_data['porez_procenat']
    zaliha.tax_exemption_reason_id = zaliha_data['tax_exemption_reason_id']
    db.session.add(zaliha)

    zalihe: List[MagacinZaliha] = db.session.query(MagacinZaliha) \
        .filter(MagacinZaliha.artikal_id == artikal_id) \
        .all()
    for zaliha in zalihe:
        zaliha.izvor_kalkulacije = zaliha_data['izvor_kalkulacije']
        zaliha.jedinicna_cijena_osnovna = zaliha_data['jedinicna_cijena_osnovna']
        zaliha.jedinicna_cijena_puna = zaliha_data['jedinicna_cijena_puna']
        zaliha.porez_procenat = zaliha_data['porez_procenat']
        zaliha.tax_exemption_reason_id = zaliha_data['tax_exemption_reason_id']

        if zaliha.magacin_id == magacin_id:
            zaliha.raspoloziva_kolicina = zaliha_data['raspoloziva_kolicina']

        db.session.add(zaliha)
    db.session.commit()

    return artikal


def delete_invoice_item_template(invoice_item_template_id):
    invoice_item_template = db.session.query(Artikal).get(invoice_item_template_id)
    invoice_item_template.is_deleted = True
    db.session.add(invoice_item_template)
    db.session.commit()


def magacin_zaliha__po_id(magacin_id: int, artikal_id: int):
    return db.session.query(MagacinZaliha) \
        .filter(MagacinZaliha.magacin_id == magacin_id) \
        .filter(MagacinZaliha.artikal_id == artikal_id) \
        .order_by(MagacinZaliha.id.desc()) \
        .first()


def artikal__trazi(pojam, firma):
    return db.session.query(Artikal) \
        .filter(Artikal.naziv.contains(pojam)) \
        .filter(Artikal.grupa_artikala.has(firma_id=firma.id)) \
        .all()


def grupa_artikala__listaj(korisnik):
    return db.session.query(GrupaArtikala) \
        .filter(GrupaArtikala.firma_id == korisnik.firma_id) \
        .all()


def listaj_grupe_artikala(firma_id):
    return db.session.query(GrupaArtikala) \
        .filter(GrupaArtikala.firma_id == firma_id) \
        .all()


def grupa_artikala__po_id__listaj(grupa_artikala_id, firma):
    return db.session.query(GrupaArtikala) \
        .filter(GrupaArtikala.id == grupa_artikala_id) \
        .filter(GrupaArtikala.firma_id == firma.id) \
        .first()


def grupa_artikala__dodaj(podaci, firma):
    grupa_artikala = GrupaArtikala()
    grupa_artikala.firma = firma
    grupa_artikala.ui_default = False
    grupa_artikala.naziv = podaci['naziv']
    grupa_artikala.boja = podaci.get('boja')

    db.session.add(grupa_artikala)
    db.session.commit()

    return grupa_artikala


def grupa_artikala__po_id__izmijeni(grupa_artikala_id, podaci, firma):
    data = {
        'naziv': podaci['naziv'],
        'boja': podaci.get('boja')
    }

    broj_izmijenjenih_redova = db.session.query(GrupaArtikala) \
        .filter(GrupaArtikala.id == grupa_artikala_id) \
        .filter(GrupaArtikala.firma_id == firma.id) \
        .update(data)

    db.session.commit()
    return broj_izmijenjenih_redova
