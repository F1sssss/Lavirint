import glob
import os
from pathlib import Path

import click

from backend.opb import csv_opb


@click.command(name='invoice:csv:clean')
@click.option('-id', '--service-id', required=True, type=int)
def csv_clean(service_id):
    csv_obrada = csv_opb.listaj_obradu_po_idu(service_id)

    for file in glob.glob(str(Path(csv_obrada.lokacija_ulaznih_csv_datoteka, '*'))):
        os.remove(file)

    for file in glob.glob(str(Path(csv_obrada.lokacija_neuspjelih_csv_datoteka, '*'))):
        os.remove(file)

    for file in glob.glob(str(Path(csv_obrada.lokacija_uspjelih_csv_datoteka, '*'))):
        os.remove(file)

    for file in glob.glob(str(Path(csv_obrada.lokacija_izlaznih_csv_datoteka, '*'))):
        os.remove(file)

    for file in glob.glob(str(Path(csv_obrada.lokacija_debug_datoteka, '*'))):
        os.remove(file)
