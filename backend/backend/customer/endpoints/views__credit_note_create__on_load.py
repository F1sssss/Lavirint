import simplejson as json

from backend.customer.auth import requires_authentication
from backend.opb import faktura_opb
from backend.opb import misc_opb
from backend.serializers import payment_method_type_schema
from backend.serializers import poreska_stopa_schema


@requires_authentication
def views__credit_note_create__on_load(operater, firma):
    poreske_stope = misc_opb.listaj_poreske_stope()
    payment_method_types = faktura_opb.get_payment_method_types()

    return json.dumps({
        'payment_method_types': payment_method_type_schema.dump(payment_method_types, many=True),
        'poreske_stope': poreska_stopa_schema.dump(poreske_stope, many=True),
    })
