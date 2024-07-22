from datetime import datetime

import bottle
import simplejson as json

from backend.customer.auth import requires_authentication
from backend.db import db
from backend.models import InvoiceSchedule
from backend.opb import faktura_opb
from backend.podesavanja import podesavanja
from backend.serializers import invoice_schedule_schema


@requires_authentication
def api__faktura__param_invoice_id__invoice_schedule__add(operater, firma, param_invoice_id):
    data = bottle.request.json.copy()

    start_datetime = data['start_datetime'].replace('Z', podesavanja.TIMEZONE)
    start_datetime = datetime.fromisoformat(start_datetime).replace(tzinfo=None)

    end_datetime = data.get('end_datetime')
    if end_datetime is not None:
        end_datetime = datetime.fromisoformat(end_datetime.replace('Z', podesavanja.TIMEZONE)).replace(tzinfo=None)

    faktura_opb.deactivate_invoice_schedules(param_invoice_id)

    invoice_schedule = InvoiceSchedule()
    invoice_schedule.start_datetime = start_datetime
    invoice_schedule.end_datetime = end_datetime
    invoice_schedule.frequency_interval = data['frequency_interval']
    invoice_schedule.source_invoice_id = param_invoice_id
    invoice_schedule.next_run_datetime = invoice_schedule.start_datetime
    invoice_schedule.last_run_datetime = None
    invoice_schedule.is_active = data['is_active']
    invoice_schedule.operater = operater
    db.session.add(invoice_schedule)
    db.session.commit()

    return json.dumps(invoice_schedule_schema.dump(invoice_schedule), **podesavanja.JSON_DUMP_OPTIONS)
