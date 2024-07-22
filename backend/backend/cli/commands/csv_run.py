import click

from backend.csv import elavirint
from backend.csv import perfekt
from backend.models import CsvObrada
from backend.opb import csv_opb


@click.command(name='csv:run')
@click.option('-id', '--obrada-id', required=True, type=int)
def csv_run(obrada_id):
    csv_obrada = csv_opb.listaj_obradu_po_idu(obrada_id)

    if csv_obrada is None:
        raise ValueError('Ne postoji obrada sa identifikatorom %s' % obrada_id)

    if csv_obrada.format_datoteke == CsvObrada.FORMAT_PERFEKT:
        perfekt.pokreni_obradu(obrada_id)
    elif csv_obrada.format_datoteke == CsvObrada.FORMAT_ELAVIRINT:
        elavirint.pokreni_obradu(obrada_id)
    else:
        raise Exception('Tip obrade ne postoji ili nije implementiran.')