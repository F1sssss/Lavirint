from typing import List

import simplejson as json

from backend.agent.auth import requires_authentication
from backend.models import Drzave, AgentUser
from backend.models import PoreskaStopa
from backend.opb import misc_opb
from backend.podesavanja import podesavanja


@requires_authentication
def controller(agent_user: AgentUser):
    countries = misc_opb.listaj_drzave()
    tax_rates = misc_opb.listaj_poreske_stope()

    return json.dumps(
        serialize_response(
            countries=countries,
            tax_rates=tax_rates
        ),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def serialize_response(
    countries: List[Drzave],
    tax_rates: List[PoreskaStopa]
):
    serialized_countries = []
    for country in countries:
        serialized_countries.append({
            'id': country.id,
            'nameMontenegrin': country.drzava,
            'nameEnglish': country.drzavaeng
        })

    serialized_tax_rates = []
    for tax_rate in tax_rates:
        serialized_tax_rates.append({
            'id': tax_rate.id,
            'percentage': tax_rate.procenat,
            'label': tax_rate.label
        })

    return {
        'countries': serialized_countries,
        'taxRates': serialized_tax_rates
    }
