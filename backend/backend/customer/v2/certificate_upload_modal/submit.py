import bottle
import pytz
import simplejson as json

from backend import exc
from backend import fiskalizacija
from backend.podesavanja import podesavanja
from backend.customer.auth import requires_authentication
from backend.models import Firma
from backend.models import Operater
from backend.opb import certificate_opb


@requires_authentication
def controller(operater: Operater, firma: Firma):
    password = bottle.request.forms.get('password')
    if not isinstance(password, str):
        return {
            "error": "Invalid password"
        }

    password = password.strip().encode('utf-8')
    if len(password) == 0:
        return {
            "error": "Invalid password"
        }

    cert_file_upload: bottle.FileUpload = bottle.request.files.get('certificate')
    if cert_file_upload is None:
        return {
            "error": "File not uploaded"
        }

    cert_bytes = cert_file_upload.file.read()

    try:
        private_key, certificate, _ = fiskalizacija.from_bytes(cert_bytes, password)
    except exc.FiscalizationException as exception:
        return {
            "error": exception.get_message()
        }

    tin, name = fiskalizacija.get_organization_data(certificate)
    if firma.pib != tin:
        return {
            "error": f"Vlasnik sertifikata je {name} ({tin}) a pokušavate dodati sertifikat za {firma.naziv} ({firma.pib})"
        }

    tz = pytz.timezone("Europe/Podgorica")

    fingerprint = fiskalizacija.get_fingerprint(certificate)

    db_certificate = certificate_opb.get_certificate_by_fingerprint(fingerprint, firma.id)
    if db_certificate is not None:
        return {
            "error": "Sertifikat već postoji."
        }

    db_certificate = certificate_opb.from_file(
        firma,
        fingerprint,
        certificate.not_valid_before.astimezone(tz),
        certificate.not_valid_after.astimezone(tz),
        fiskalizacija.encrypt_password(password),
    )

    fiskalizacija.to_certificate_store(fingerprint.decode(), cert_bytes)

    return json.dumps({
        "certificate_expiration_date": certificate_opb.get_expiration_date(firma)
    }, **podesavanja.JSON_DUMP_OPTIONS)