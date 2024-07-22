import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from backend import stampa
from backend.logging import logger

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def is_valid_mail(email):
    return re.fullmatch(email_regex, email)


def test_smtp_connection(host, port, username, password):
    try:
        logger.info("Starting SMTP session")
        smtp = smtplib.SMTP_SSL(host, port, timeout=1)
    except (smtplib.SMTPException, Exception):
        logger.exception("Failed to create SMTP session due to SMTPException")
        return False

    try:
        smtp.ehlo()
    except (smtplib.SMTPException, Exception):
        logger.exception("Failed EHLO due to SMTPException")
        return False

    noop_result = smtp.noop()
    if noop_result[0] != 250:
        logger.info(noop_result)
        return False

    try:
        smtp.login(username, password)
    except (smtplib.SMTPException, Exception):
        logger.exception('Failed SMTP login')
        return False

    quit_result = smtp.quit()
    if quit_result[0] != 221:
        logger.info(quit_result)
        return False

    if smtp.sock is not None:
        logger.info("Socket not closed")
        return False

    return True


def send_invoice_mail(invoice, host, port, mail_from, username, password, mail_to):
    body = "Poštovani,\n" \
           "\n" \
           "u prilogu je faktura.\n" \
           "\n" \
           "Srdačan pozdrav"

    mail = MIMEMultipart()
    mail['From'] = mail_from
    mail['To'] = mail_to
    mail['Date'] = formatdate(localtime=True)
    mail['Subject'] = 'Faktura br. %s' % invoice.efi_ordinal_number
    mail.attach(MIMEText(body, 'plain'))

    pdf_name = 'Faktura br. %s.pdf' % invoice.efi_ordinal_number

    payload = MIMEBase('application', 'octate-stream', Name=pdf_name)
    pdf_content = stampa.get_invoice_template_pdf_as_bytes(faktura=invoice, tip_stampe='a4')
    payload.set_payload(pdf_content)

    encoders.encode_base64(payload)

    payload.add_header('Content-Decomposition', 'attachment', filename=pdf_name)
    mail.attach(payload)

    try:
        session = smtplib.SMTP_SSL(host, port)
        session.ehlo()
        session.login(username, password)
        session.sendmail(mail['From'], mail['To'], mail.as_string())
        session.close()

        logger.info('Mail sent')
    except Exception as exception:
        logger.exception('Greška prilikom slanja mejla')
        raise exception
