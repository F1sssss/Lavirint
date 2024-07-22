import click
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from backend.opb import soap_opb
from backend.soap_api import elavirint_xml


@click.command(name='invoice:xml:parse')
@click.option('-u', '--username', required=True)
@click.option('-p', '--password', required=True, prompt=True, hide_input=True)
@click.option('-i', '--input', 'input_file', required=True, type=click.File('rb'))
def invoice_xml_parse(username, password, input_file):
    soap_user = soap_opb.get_soap_user_by_username(username)
    if soap_user is None:
        click.echo(f'No SOAP user with username {username}')

    if not pbkdf2_sha256.verify(password, soap_user.password):
        click.echo('Combination of username and password is invalid')

    data, _, _ = elavirint_xml.soap_xml_to_invoice_dict(soap_user, input_file.read())

    click.echo(data)
