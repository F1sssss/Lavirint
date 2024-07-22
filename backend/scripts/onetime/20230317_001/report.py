from datetime import datetime
from datetime import timedelta

import pdfkit
from bottle import SimpleTemplate

from backend import models as m
from backend.db import db
from backend.opb import report_opb

operater = db.session.query(m.Operater).get(108)
naplatni_uredjaj = db.session.query(m.NaplatniUredjaj).get(721)

datum_od = datetime.strptime('2022-01-01T00:00:00.000Z', "%Y-%m-%dT%H:%M:%S.%fZ")
datum_do = datetime.strptime('2023-01-01T00:00:00.000Z', "%Y-%m-%dT%H:%M:%S.%fZ")

data = report_opb.izvjestaj__stanje(
    naplatni_uredjaj,
    operater,
    operater.firma,
    datum_od,
    datum_do,
    report_opb.REPORT_TYPE_PERIODIC_REPORT
)

with open('stanje.html', 'r') as file:
    template = SimpleTemplate(file.read(), encoding='utf-8').render(**{
        **data,
        'datum_od': datum_od,
        'datum_do': datum_do - timedelta(seconds=1)
    })

    pdfkit.from_string(template, './report.pdf', options={
        'zoom': '1.275',
        'margin-top': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'margin-right': '0mm',
    })