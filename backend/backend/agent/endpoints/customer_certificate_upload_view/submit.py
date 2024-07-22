import bottle
import pytz
import simplejson as json

from backend import exc
from backend import fiskalizacija
from backend.podesavanja import podesavanja
from backend.agent.auth import requires_authentication
from backend.models import AgentUser
from backend.opb import certificate_opb
from backend.opb import firma_opb


@requires_authentication
def controller(agent_user: AgentUser):
    customer_id = bottle.request.forms.get('customerId')
    if customer_id is None:
        return {
            "error": "Missing required parameter"
        }
    customer = firma_opb.get_company_by_id(customer_id)

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
    if customer.pib != tin:
        return {
            "error": "Vlasnik sertifikata je " + name + " a pokušavate dodati sertifikat za " + customer.naziv
        }

    tz = pytz.timezone("Europe/Podgorica")

    fingerprint = fiskalizacija.get_fingerprint(certificate)

    db_certificate = certificate_opb.get_certificate_by_fingerprint(fingerprint, customer.id)
    if db_certificate is not None:
        return {
            "error": "Navedeni sertifikat je već postavljen za firmu " + customer.naziv
        }

    db_certificate = certificate_opb.from_file(
        customer,
        fingerprint,
        certificate.not_valid_before.astimezone(tz),
        certificate.not_valid_after.astimezone(tz),
        fiskalizacija.encrypt_password(password),
    )

    fiskalizacija.to_certificate_store(fingerprint.decode(), cert_bytes)

    return json.dumps({}, **podesavanja.JSON_DUMP_OPTIONS)