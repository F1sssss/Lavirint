import uuid as uuid_gen
from datetime import datetime
from pathlib import Path

import pytz
import requests

from backend import efi_xml
from backend import fiskalizacija
from backend.db import db
from backend.models import Depozit
from backend.models import RegisterDepositRequest
from backend.models import RegisterDepositResponse
from backend.opb import certificate_opb
from backend.opb import faktura_opb
from backend.opb import helpers
from backend.podesavanja import podesavanja


def listaj_danasnji_depozit(naplatni_uredjaj_id):
    day_start, next_day_start = helpers.danas_filteri()

    return db.session.query(Depozit) \
        .filter(Depozit.datum_kreiranja >= day_start) \
        .filter(Depozit.datum_kreiranja < next_day_start) \
        .filter(Depozit.naplatni_uredjaj_id == naplatni_uredjaj_id) \
        .filter(Depozit.tip_depozita == Depozit.TIP_DEPOZITA_INITIAL) \
        .first()


def depozit__dodaj(podaci, firma, operater):

    if faktura_opb.exists_at_least_one_cash_invoice_for_current_day(operater.naplatni_uredjaj_id):
        return {
            'poruka': 'Depozit se ne može promijeniti nakon registracije.'
        }

    danasnji_depozit = listaj_danasnji_depozit(operater.naplatni_uredjaj_id)

    if danasnji_depozit is not None:
        danasnji_depozit.iznos = podaci['iznos']
        db.session.commit()
        return danasnji_depozit

    depozit = Depozit(**podaci)
    depozit.operater = operater
    depozit.firma = operater.firma
    depozit.je_pocetak_dana = True
    depozit.tip_depozita = Depozit.TIP_DEPOZITA_INITIAL
    depozit.status = 1
    depozit.naplatni_uredjaj = operater.naplatni_uredjaj

    db.session.add(depozit)
    db.session.commit()

    return depozit


def depozit__podigni(podaci, firma, operater):
    stanje = helpers.dohvati_stanje(operater.naplatni_uredjaj_id)

    if stanje['ukupno'] < float(podaci['iznos']):
        return {
            'poruka': 'Pokušaj povlačenja više novca od raspoloživog'
        }

    depozit = Depozit(**podaci)
    depozit.operater = operater
    depozit.firma = operater.firma
    depozit.je_pocetak_dana = True
    depozit.tip_depozita = Depozit.TIP_DEPOZITA_WITHDRAW
    depozit.naplatni_uredjaj = operater.naplatni_uredjaj
    db.session.add(depozit)

    return efi_prijava_depozita(depozit, firma)


def get_todays_deposits() -> object:
    day_start, next_day_start = helpers.danas_filteri()

    return db.session \
        .query(Depozit) \
        .filter(Depozit.status == Depozit.STATUS_FISCALISE_SUCCESS) \
        .filter(Depozit.datum_kreiranja >= day_start) \
        .filter(Depozit.datum_kreiranja < next_day_start) \
        .all()


def efi_prijava_depozita(depozit, firma):
    timestamp = datetime.now().astimezone(tz=pytz.timezone("Europe/Podgorica"))
    depozit.datum_slanja = timestamp
    depozit.status = 1
    db.session.commit()

    request = RegisterDepositRequest()
    request.uuid = str(uuid_gen.uuid4())
    request.depozit = depozit

    db_certificate = certificate_opb.get_certificate_by_customer(depozit.firma, timestamp)
    if db_certificate is None:
        return {
            'greska': 'Nije moguće potpisati prijavu depozita jer ne postoji ispravan sertifikat za potpisavanje za aktuelni period.'
        }

    xml = efi_xml.generate_register_cash_deposit_request(request, depozit, firma)
    private_key, certificate, _ = fiskalizacija.from_certificate_store(db_certificate.fingerprint, db_certificate.password)
    finalized_xml = fiskalizacija.potpisi(xml, private_key, certificate)

    request.xml = finalized_xml
    db.session.add(request)
    db.session.commit()

    if podesavanja.EFI_FILES_STORE is not None:
        with open(Path(podesavanja.EFI_FILES_STORE, 'depozit__%s__request.xml' % depozit.id), 'wb') as file:
            file.write(efi_xml.tostring(finalized_xml))

    try:
        http_response = requests.post(podesavanja.EFI_SERVICE_URL, data=efi_xml.tostring(finalized_xml), verify=False, headers={
            'Content-Type': 'text/xml; charset=utf-8'
        })
    except requests.ConnectionError:
        return {
            'greska': 'Greška prilikom povezivanja sa portalom poreske uprave.'
        }

    try:
        if podesavanja.EFI_FILES_STORE is not None:
            with open(Path(podesavanja.EFI_FILES_STORE, 'depozit__%s__response.xml' % depozit.id), 'wb') as file:
                file.write(http_response.content)
                file.close()

        response = RegisterDepositResponse()
        response.depozit = depozit
        response.register_deposit_request = request
        response.xml = http_response.content.decode()

        uuid, faultcode, faultstring, fcdc = efi_xml.read_register_deposit_response(response.xml)
        response.uuid = uuid
        if faultcode is None:
            depozit.fiskalizacioni_kod = fcdc
            depozit.status = 2
        else:
            response.faultcode = faultcode
            response.faultstring = faultstring
            depozit.status = 3

        request.register_deposit_response = response
        db.session.add(response)
        db.session.commit()

        if fcdc is not None:
            return depozit
        else:
            return {
                'greska': efi_xml.xml_error_to_string(faultcode)
            }
    except Exception as e:
        return {
            'greska': str(e)
        }
