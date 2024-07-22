import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.serializers import payment_method_type_schema


@requires_authentication
def api__modal__invoice_filter(operater, firma):
    payment_method_types = faktura_opb.get_payment_method_types()

    return json.dumps({
        'payment_method_types': payment_method_type_schema.dump(payment_method_types, many=True),
    })
