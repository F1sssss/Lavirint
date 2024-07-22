from datetime import datetime
from typing import Optional

import pytz

from backend.db import db
from backend.models import Firma
from backend.models import FiscalizationCertificate


def from_file(
    company: Firma, fingerprint: str, not_valid_before: datetime, not_valid_after: datetime, password: bytes
) -> FiscalizationCertificate:
    new_certificate = FiscalizationCertificate()
    new_certificate.fingerprint = fingerprint
    new_certificate.not_valid_before = not_valid_before
    new_certificate.not_valid_after = not_valid_after
    new_certificate.password = password
    new_certificate.owner_id = company.id
    db.session.add(new_certificate)
    db.session.commit()

    recheck_certificate(company, datetime.now())

    return new_certificate


def valid(certificate: FiscalizationCertificate, timestamp: datetime) -> bool:
    tz = pytz.timezone("Europe/Podgorica")
    return certificate.not_valid_before.astimezone(tz=tz) < timestamp.astimezone(tz=tz) < certificate.not_valid_after.astimezone(tz=tz)


def recheck_certificate(company: Firma, timestamp: datetime) -> Optional[FiscalizationCertificate]:
    company.current_certificate = get_certificate_by_timestamp(company, timestamp)
    if company.current_certificate is None:
        company.next_certificate = None
    else:
        company.next_certificate = get_certificate_by_timestamp(
            company, company.current_certificate.not_valid_after
        )

    db.session.commit()

    return company.current_certificate


def get_certificate_by_customer(customer: Firma, timestamp: datetime):
    if customer.current_certificate is None or not valid(customer.current_certificate, timestamp):
        recheck_certificate(customer, timestamp)

    return customer.current_certificate


def get_certificate_by_timestamp(company: Firma, timestamp: datetime) -> Optional[FiscalizationCertificate]:
    return (
        db.session.query(FiscalizationCertificate)
        .filter(FiscalizationCertificate.not_valid_before < timestamp)
        .filter(timestamp < FiscalizationCertificate.not_valid_after)
        .filter(FiscalizationCertificate.owner_id == company.id)
        .order_by(FiscalizationCertificate.not_valid_before)
        .first()
    )


def get_certificate_by_fingerprint(fingerprint: str, owner_id: int):
    return (
        db.session.query(FiscalizationCertificate)
        .filter(FiscalizationCertificate.fingerprint == fingerprint)
        .filter(FiscalizationCertificate.owner_id == owner_id)
        .first()
    )


def delete_certificate(certificate: FiscalizationCertificate):
    if certificate.owner.current_certificate is not None and certificate.owner.current_certificate.id == certificate.id:
        db.session.add(certificate.owner.current_certificate)
        certificate.owner.current_certificate = None
    if certificate.owner.next_certificate is not None and certificate.owner.next_certificate.id == certificate.id:
        db.session.add(certificate.owner.current_certificate)
        certificate.owner.current_certificate = None
    db.session.commit()

    db.session.delete(certificate)
    db.session.commit()


def get_certificate_by_id(certificate_id: int):
    return db.session.get(FiscalizationCertificate, certificate_id)


def get_expiration_date(customer: Firma):
    if customer.next_certificate_id is not None:
        return customer.next_certificate.not_valid_after.isoformat()
    elif customer.current_certificate_id is not None:
        return customer.current_certificate.not_valid_after.isoformat()
    else:
        return None
