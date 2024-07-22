import click

from backend.cli.commands.casper_email_send import casper_email_send
from backend.cli.commands.casper_email_create import casper_email_create
from backend.cli.commands.certificate_info import certificate_info
from backend.cli.commands.csv_clean import csv_clean
from backend.cli.commands.csv_load import csv_load
from backend.cli.commands.csv_run import csv_run
from backend.cli.commands.invoice_schedule import invoice_schedule
from backend.cli.commands.invoice_xml_parse import invoice_xml_parse
from backend.cli.commands.user_password_generate import user_password_generate


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(casper_email_create)
    cli.add_command(casper_email_send)
    cli.add_command(certificate_info)
    cli.add_command(csv_clean)
    cli.add_command(csv_load)
    cli.add_command(csv_run)
    cli.add_command(invoice_schedule)
    cli.add_command(invoice_xml_parse)
    cli.add_command(user_password_generate)
    cli()
