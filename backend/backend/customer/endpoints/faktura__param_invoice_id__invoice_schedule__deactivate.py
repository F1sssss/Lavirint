from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb


@requires_authentication
def api__faktura__param_invoice_id__invoice_schedule__deactivate(operater, firma, param_invoice_id):
    faktura_opb.deactivate_invoice_schedules(param_invoice_id)
