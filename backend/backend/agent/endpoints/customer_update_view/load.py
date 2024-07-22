import bottle
import simplejson as json

from backend.agent.auth import requires_authentication
from backend.models import Firma, AgentUser
from backend.opb import firma_opb
from backend.podesavanja import podesavanja


@requires_authentication
def controller(agent_user: AgentUser):
    post_data = bottle.request.json.copy()
    company = firma_opb.get_company_by_id(post_data['companyId'])
    return json.dumps(
        serizalize_response(company),
        **podesavanja.JSON_DUMP_OPTIONS
    )


def serizalize_response(company: Firma):
    r = {
        'id': company.id,
        'name': company.naziv,
        'isActive': company.je_aktivna,
        'identificationNumber': company.pib,
        'taxNumber': company.pdvbroj,
        'isTaxpayer': company.je_poreski_obaveznik,
        'address': company.adresa,
        'city': company.grad,
        'bankAccount': company.ziroracun,
        'phoneNumber': company.telefon,
        'emailAddress': company.email,
        'countryId': None,
        'country': None
    }

    if company.drzave is not None:
        r['countryId'] = company.drzave.id
        r['country'] = {
            'id': company.drzave.id,
            'nameMontenegrin': company.drzave.drzava,
            'nameEnglish': company.drzave.drzavaeng
        }

    return {
        'company': r
    }
