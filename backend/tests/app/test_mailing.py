import pytest

import backend.core.mailing as mailing
from backend.db import db
from backend.models import Faktura


@pytest.mark.skip(reason="skipped as to not distrub the owner of email address")
def test_smtp_connection():
    is_success = mailing.test_smtp_connection(
        host='smtp.gmail.com',
        port=465,
        username='caspermnedoo@gmail.com',
        password='Jovana123!')
    assert is_success


@pytest.mark.skip(reason="skipped as to not distrub the owner of email address")
def test_send_invoice_mail():
    invoice = db.session.query(Faktura).get(1)

    mailing.send_invoice_mail(
        invoice=invoice,
        host='smtp.gmail.com',
        port=465,
        username='caspermnedoo@gmail.com',
        password='Jovana123!',
        mail_from='caspermnedoo@gmail.com',
        mail_to='isdjuka@gmail.com'
    )
