import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import artikal_opb


@requires_authentication
def api__artikal__param_artikal_id__obrisi(operater, firma, param_artikal_id):
    try:
        artikal_opb.delete_invoice_item_template(param_artikal_id)
        return json.dumps({
            'is_success': True
        })
    except Exception:
        return json.dumps({
            'is_success': False
        })