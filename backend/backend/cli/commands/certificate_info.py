import click
from cryptography.fernet import Fernet

from backend import fiskalizacija
from backend.opb import firma_opb
from backend.podesavanja import podesavanja


@click.command(name='certificate:info')
@click.option('--id', 'id_type', flag_value='id', help='Get info by company id')
@click.option('--tin', 'id_type', flag_value='tin', help='Get info by company tin')
@click.argument('id_number', required=True)
def certificate_info(id_number, id_type):

    if id_type == 'tin':
        company = firma_opb.listaj_po_pibu(id_number)
        if company is None:
            click.echo(f"Company with TIN {id_number} does not exist.")
            return
    elif id_type == 'id':
        company = firma_opb.get_company_by_id(id_number)
        if company is None:
            click.echo(f"Company with TIN {id_number} does not exist.")
            return
    else:
        raise click.exceptions.BadParameter('Id type is not set. Must use an option --id or --tin to set id type.')

    password = Fernet(podesavanja.KALAUZ).decrypt(company.certificate_password.encode()).decode()

    click.echo()
    click.echo(f'id:       {company.id}')
    click.echo(f'tin:      {company.pib}')
    click.echo(f'name:     {company.naziv}')
    click.echo(f'password: {password}')
    click.echo(f'path:     {fiskalizacija.get_certificate_path(company.pib)}')
    click.echo()
