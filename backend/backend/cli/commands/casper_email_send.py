import time

import click

from backend.core import mailing
from backend.models import FakturaMailKampanjaStavka
from backend.opb import faktura_opb


@click.command(name='casper:email:send')
@click.option('-c', '--campaign-id', type=int, required=True)
@click.option('-d', '--dry-run', 'is_dry_run', is_flag=True)
def casper_email_send(campaign_id, is_dry_run):
    kampanja = faktura_opb.get_mailing_campaign_by_id(campaign_id)
    if kampanja is None:
        click.echo('Email campgain with id %s does not exist' % campaign_id)
        return

    stavke = faktura_opb.get_mailing_campaign_item_by_id(campaign_id)

    timeout_counter = 0
    total_items = len(stavke)
    for index, stavka in enumerate(stavke):
        if stavka.status == FakturaMailKampanjaStavka.STATUS_SUCCESS:
            click.echo(
                f'[{index+1}/{total_items}]. '
                f'Skipping invoice {stavka.faktura.id} from {stavka.mail_from} to {stavka.mail_to}'
                f'because it is already sent.')
            click.echo()
            continue
        elif stavka.status == FakturaMailKampanjaStavka.STATUS_FAIL_ON_CREATE:
            click.echo(
                f'[{index+1}/{total_items}]. '
                f'Skipping invoice {stavka.faktura.id} because it has error. '
                f'Error message: {stavka.opis_greske}')
            click.echo()
            continue

        click.echo(
            f'[{index+1}/{total_items}]. '
            f'Sending invoice {stavka.faktura.id} from {stavka.mail_from} to {stavka.mail_to}. ', nl=False)
        if not is_dry_run:
            try:
                mailing.send_invoice_mail(
                    invoice=stavka.faktura,
                    host='smtp.gmail.com',
                    port=465,
                    mail_from='caspermnedoo@gmail.com',
                    username='caspermnedoo@gmail.com',
                    password='Jovana123!',
                    mail_to=stavka.mail_to
                )
                faktura_opb.set_mailing_campaign_id_success(stavka)
                click.echo('Success.')
                click.echo()
            except Exception as exception:
                error_message = str(exception)
                faktura_opb.set_mailing_campaign_id_fail(stavka, error_message[:500])
                click.echo(f'Failed. Error message: {str(exception)}')
                click.echo()

        timeout_counter += 1
        if timeout_counter == 10:
            timeout_counter = 0
            time.sleep(30)
            click.echo('Waiting 30 seconds until next batch.')
            click.echo()
