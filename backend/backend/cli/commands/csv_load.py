import click

from backend.csv import elavirint
from backend.csv import perfekt
from backend.models import CsvObrada
from backend.opb import csv_opb


@click.command(name='csv:load')
@click.option('-id', '--obrada-id', required=True, type=int)
@click.option('-f', '--filepath', required=True, type=click.Path())
def csv_load(obrada_id, filepath):
    processing = csv_opb.listaj_obradu_po_idu(obrada_id)
    if processing is None:
        click.echo(f'Nema CSV obrade sa id-em {obrada_id}')

    if processing.format_datoteke == CsvObrada.FORMAT_ELAVIRINT:
        podaci, firma, operater, naplatni_uredjaj, faktura_za_korekciju = (
            elavirint.load_invoice_csv(processing, filepath))
        click.echo(podaci)
    elif processing.format_datoteke == CsvObrada.FORMAT_PERFEKT:
        podaci, firma, operater, naplatni_uredjaj, faktura_za_korekciju = (
            perfekt.procitaj_fakturu_iz_csv_datoteke(processing, filepath))
        click.echo(podaci)
    else:
        click.echo(f'Unhandled CSV file format.')
