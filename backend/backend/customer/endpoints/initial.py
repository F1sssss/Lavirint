from typing import List

import simplejson as json

from backend.customer.auth import requires_authentication
from backend.models import Drzave
from backend.models import JedinicaMjere
from backend.models import Operater
from backend.models import PaymentMethodType
from backend.models import PoreskaStopa
from backend.models import TaxExemptionReason
from backend.models import TipIdentifikacioneOznake
from backend.models import Valuta
from backend.opb import certificate_opb
from backend.opb import faktura_opb
from backend.opb import misc_opb
from backend.podesavanja import podesavanja
from backend.serializers import jedinica_mjere_schema
from backend.serializers import operater_schema
from backend.serializers import payment_method_type_schema
from backend.serializers import poreska_stopa_schema
from backend.serializers import tax_exemption_reason_schema
from backend.serializers import valuta_schema


@requires_authentication
def api__frontend__initial(operater, firma):
    jedinice_mjere = faktura_opb.jedinica_mjere__listaj(firma)
    tax_exemption_reasons = faktura_opb.get_active_tax_exemption_reasons()
    valute = misc_opb.valuta__listaj()
    payment_method_types = faktura_opb.get_payment_method_types()
    poreske_stope = misc_opb.listaj_poreske_stope()
    drzave = misc_opb.listaj_drzave()
    tipovi_identifikacione_oznake = misc_opb.listaj_tipove_identifikacione_oznake()

    return json.dumps(
        serialize_response(
            customer_user=operater,
            units_of_measurement=jedinice_mjere,
            tax_exemption_reasons=tax_exemption_reasons,
            currencies=valute,
            payment_method_types=payment_method_types,
            tax_rates=poreske_stope,
            countries=drzave,
            identification_types=tipovi_identifikacione_oznake
        ),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def serialize_response(
        customer_user: Operater,
        units_of_measurement: List[JedinicaMjere],
        tax_exemption_reasons: List[TaxExemptionReason],
        currencies: List[Valuta],
        payment_method_types: List[PaymentMethodType],
        tax_rates: List[PoreskaStopa],
        countries: List[Drzave],
        identification_types: List[TipIdentifikacioneOznake]
):
    serialized_countries = []
    for country in countries:
        serialized_countries.append({
            'id': country.id,
            'drzava_skraceno_2': country.drzava_skraceno_2,
            'drzava_skraceno_3': country.drzava_skraceno_3,
            'drzava': country.drzava,
            'drzavaeng': country.drzavaeng,
        })

    serialized_id_types = []
    for id_type in identification_types:
        serialized_id_types.append({
            'id': id_type.id,
            'naziv': id_type.naziv
        })

    return {
        'certificate_expiration_date': certificate_opb.get_expiration_date(customer_user.firma),
        'korisnik': operater_schema.dump(customer_user),
        'jedinice_mjere': jedinica_mjere_schema.dump(units_of_measurement, many=True),
        'tax_exemption_reasons': tax_exemption_reason_schema.dump(tax_exemption_reasons, many=True),
        'valute': valuta_schema.dump(currencies, many=True),
        'payment_method_types': payment_method_type_schema.dump(payment_method_types, many=True),
        'poreske_stope': poreska_stopa_schema.dump(tax_rates, many=True),
        'countries': serialized_countries,
        'identification_types': serialized_id_types
    }
