import click

from backend.core import mailing
from backend.db import db
from backend.models import Faktura
from backend.models import FakturaMailKampanja
from backend.models import FakturaMailKampanjaStavka


@click.command(name='casper:email:create')
@click.option('-s', '--start-date', type=click.DateTime(formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']),
              help='Start date for filtering invoices, inclusive', required=True)
@click.option('-e', '--end-date', type=click.DateTime(formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']),
              help='End date for filtering invoices, exclusive', required=True)
@click.option('-d', '--dry-run', 'is_dry_run', is_flag=True)
def casper_email_create(start_date, end_date, is_dry_run):
    sender_email = 'caspermnedoo@gmail.com'

    fakture = db.session.query(Faktura) \
        .filter(Faktura.firma_id == 231) \
        .filter(Faktura.tip_fakture_id == Faktura.TYPE_REGULAR) \
        .filter(Faktura.status == Faktura.STATUS_FISCALISATION_SUCCESS) \
        .filter(Faktura.datumfakture >= start_date) \
        .filter(Faktura.datumfakture < end_date) \
        .filter(Faktura.komitent_id.isnot(None)) \
        .all()

    kampanja = FakturaMailKampanja()
    kampanja.datum_pocetka = start_date
    kampanja.datum_zavrsetka = end_date
    kampanja.firma_id = 231

    total_invoices = len(fakture)
    for index, faktura in enumerate(fakture):
        click.echo(f'[{index + 1}/{total_invoices}]', nl=False)
        click.echo(f'Creating notification for invoice {faktura.id}')

        mail = FakturaMailKampanjaStavka()
        mail.komitent_id = faktura.komitent_id
        mail.faktura = faktura
        mail.mail_from = sender_email
        mail.mail_to = None
        mail.faktura_mail_kampanja = kampanja
        mail.status = FakturaMailKampanjaStavka.STATUS_PENDING

        if faktura.komitent.email is None:
            mail.status = FakturaMailKampanjaStavka.STATUS_FAIL_ON_CREATE
            mail.opis_greske = 'Kupac nema definisanu e-mail adresu.'
            click.echo(f'Failed, recipient e-mail address is missing.')
            db.session.add(mail)
            continue

        mail_to = faktura.komitent.email.strip()
        if len(mail_to) == 0:
            mail.status = FakturaMailKampanjaStavka.STATUS_FAIL_ON_CREATE
            mail.opis_greske = 'Kupac nema definisanu e-mail adresu.'
            click.echo(f'Error: Recipient e-mail address is missing.')
            db.session.add(mail)
            continue

        if not mailing.is_valid_mail(mail_to):
            mail.status = FakturaMailKampanjaStavka.STATUS_FAIL_ON_CREATE
            mail.opis_greske = 'E-mail adresa kupca nije ispravna.'
            click.echo(f'Error: Recipient mail address "{mail_to}" is invalid.')
            db.session.add(mail)
            continue

    if not is_dry_run:
        db.session.commit()
