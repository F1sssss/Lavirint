import binascii
import os
import shutil
from datetime import datetime
from pathlib import Path

import pytz
from cryptography import x509
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import pkcs12
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import column
from sqlalchemy import table

from backend.db import db
from backend.podesavanja import podesavanja

seller_table = table(
    "firma",
    column("id", Integer),
    column("pib", String),
    column("certificate_password", String)
)

cert_table = table(
    "fiscalization_certificate",
    column("id", Integer),
    column("fingerprint", String),
    column("not_valid_after", DateTime),
    column("not_valid_before", DateTime),
    column("owner_id", Integer),
    column("password", String)
)

sellers = db.session.execute(seller_table.select())

for seller in sellers:
    seller_id = seller[0]
    seller_tin = seller[1]
    seller_certificate_password = seller[2]

    if seller_certificate_password is None:
        continue

    cert_path = Path(podesavanja.CLIENT_CERTIFICATE_STORE, 'old', f'{seller_tin}.pfx')
    if not os.path.exists(cert_path):
        continue

    with open(cert_path, 'rb') as file:
        cert_bytes = file.read()
    cert_password = Fernet(podesavanja.KALAUZ).decrypt(seller_certificate_password.encode())

    try:
        private_key, certificate, _ = pkcs12.load_key_and_certificates(cert_bytes, cert_password)
    except ValueError as exception:
        if str(exception) == "Could not deserialize PKCS12 data":
            print("Nije moguće raspokovati sertifikat. Neispravna datoteka. Firma: %s" % seller_id)
        elif str(exception) == "Invalid password or PKCS12 data":
            print("Nije moguće raspokovati sertifikat. Neispravna lozinka. Firma: %s" % seller_id)
        else:
            print("Nije moguće raspokovati sertifikat. Nepoznata greška. Firma: %s" % seller_id)
        continue

    cert_fingerprint = binascii.hexlify(certificate.fingerprint(hashes.SHA256()))
    new_cert_path = Path(podesavanja.CLIENT_CERTIFICATE_STORE, f"{cert_fingerprint.decode()}.pfx")


    result = db.session.execute(
        cert_table.insert().values({
            "fingerprint": cert_fingerprint,
            "not_valid_after": certificate.not_valid_after.astimezone(pytz.timezone('Europe/Podgorica')),
            "not_valid_before": certificate.not_valid_before.astimezone(pytz.timezone('Europe/Podgorica')),
            "owner_id": seller.id,
            "password": seller_certificate_password
        })
    )
    db.session.commit()

    # copy file to new location
    shutil.copy(cert_path, new_cert_path)


db.session.close()
