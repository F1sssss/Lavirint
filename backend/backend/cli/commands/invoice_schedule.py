from datetime import datetime

import click

from backend.opb import faktura_opb


@click.command(name='invoice:schedule')
@click.option(
    '-d', '--run-datetime', 'run_datetime',
    type=click.DateTime(formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']),
    default=datetime.now())
def invoice_schedule(run_datetime):
    active_invoice_schedules = faktura_opb.get_active_invoice_schedules()

    for invoice_schedule in active_invoice_schedules:
        faktura_opb.make_regular_invoice_from_invoice_schedule(invoice_schedule, run_datetime)
