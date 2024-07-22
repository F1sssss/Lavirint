import binascii
import hashlib
import os
from pathlib import Path
from typing import Union

from cryptography import x509
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization import pkcs12
from signxml import XMLSigner

from backend import exc
from backend.podesavanja import podesavanja

OID_ORGANIZATION_IDENTIFIER = x509.ObjectIdentifier("2.5.4.97")
OID_ORGANIZATION_NAME = x509.ObjectIdentifier("2.5.4.10")


def get_certificate_path(fingerprint: str) -> Path:
    return Path(podesavanja.CLIENT_CERTIFICATE_STORE, f'{fingerprint}.pfx')


def to_certificate_store(fingerprint: Union[str, Path], cert_bytes: bytes):
    filepath = get_certificate_path(fingerprint)
    with open(filepath, 'wb') as file:
        file.write(cert_bytes)


def encrypt_password(password: bytes) -> bytes:
    key = Fernet(podesavanja.KALAUZ)
    return key.encrypt(password)


def decrypt_password(password: str) -> bytes:
    key = Fernet(podesavanja.KALAUZ)
    return key.decrypt(password.encode())


def from_certificate_store(fingerprint: str, password: str):
    pfx_lokacija = get_certificate_path(fingerprint)
    with open(pfx_lokacija, 'rb') as file:
        return pkcs12.load_key_and_certificates(file.read(), password=decrypt_password(password))


def from_bytes(cert_bytes: bytes, password: bytes):
    try:
        return pkcs12.load_key_and_certificates(cert_bytes, password=password)
    except ValueError as exception:
        if str(exception) == "Could not deserialize PKCS12 data":
            raise exc.CertificateDecryptionInvalidFile()
        elif str(exception) == "Invalid password or PKCS12 data":
            raise exc.CertificateDecryptionInvalidPassword()
        else:
            raise exc.CertificateDecryptionUnknownException()


def get_organization_data(certificate) -> (str, str):
    tin = None
    name = None
    for attribute in certificate.subject:
        if attribute.oid == OID_ORGANIZATION_IDENTIFIER:
            tin = attribute.value.replace("VATME-", "")
        if attribute.oid == OID_ORGANIZATION_NAME:
            name = attribute.value.replace("VATME-", "")

    return tin, name


def get_iic_digest_and_signature(data: bytes, private_key):
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return (
        hashlib.md5(signature).hexdigest(),
        binascii.b2a_hex(signature).decode()
    )


def potpisi(xml, private_key: RSAPrivateKey, certificate: x509):
    signer = XMLSigner(c14n_algorithm=u'http://www.w3.org/2001/10/xml-exc-c14n#')
    signer.namespaces = {
        None: 'http://www.w3.org/2000/09/xmldsig#'
    }

    # private_key_pem = private_key.private_bytes(
    #     encoding=serialization.Encoding.PEM,
    #     format=serialization.PrivateFormat.PKCS8,
    #     encryption_algorithm=serialization.NoEncryption()
    # )
    #
    # certificate_pem = (
    #     certificate
    #     .public_bytes(serialization.Encoding.PEM)
    #     .decode('utf-8')
    # )

    return signer.sign(
        xml,
        key=private_key,
        cert=[certificate],
        reference_uri="Request",
        id_attribute="Id"
    )


def get_fingerprint(certificate: x509):
    return binascii.hexlify(certificate.fingerprint(hashes.SHA256()))
