import bottle

import simplejson as json

from backend.podesavanja import podesavanja
from backend.agent import validators
from backend.agent.auth import requires_authentication
from backend.models import AgentUser
from backend.opb import firma_opb


@requires_authentication
def controller(agent_user: AgentUser):
    error_message, data = validate_data(bottle.request.json.copy())
    if error_message is not None:
        return json.dumps({
            'errorMessage': error_message
        }, **podesavanja.JSON_DUMP_OPTIONS)

    firma_opb.insert_company(data)

    return json.dumps({
        'errorMessage': None,
    }, **podesavanja.JSON_DUMP_OPTIONS)


def validate_data(data: dict):
    output = {}
    try:
        output['naziv'] = validators.string(data.get('name'))
    except (Exception, ) as exception:
        # logger.error('Invalid parameter "name".')
        return 'Polje "Naziv" mora biti popunjeno.', None

    try:
        output['pib'] = validators.company_id_number(data.get('identificationNumber'))
    except (Exception, ) as exception:
        # looger.error('Invalid parameter "identificationNumber".')
        return 'Polje "Identifikaciona oznaka" mora biti popunjeno.', None

    try:
        output['pdvbroj'] = validators.string(data.get('taxNumber'), allow_none=True)
    except (Exception, ) as exception:
        return 'Polje "PDV broj" mora biti tekstualno polje.', None

    try:
        output['adresa'] = validators.string(data.get('address'))
    except (Exception, ) as exception:
        # logger.error('Invalid parameter "address"')
        return 'Polje "Adresa" mora biti popunjeno.', None

    try:
        output['grad'] = validators.string(data.get('city'))
    except (Exception, ) as exception:
        # logger.error('Invalid parameter "city"')
        return 'Polje "Grad" mora biti popunjeno.', None

    try:
        country = validators.country(data.get('countryId'))
        output['drzava'] = country.id
    except (Exception, ) as exception:
        # logger.error('Invalid parameter "countryId"')
        return 'Polje "Država" ne smije biti prazno polje.', None

    try:
        output['je_aktivna'] = validators.boolean(data.get('isActive'))
    except (Exception, ) as exception:
        # logger.error('Invalid parameter "isActive"')
        return 'Polje "Je aktivan?" mora biti "Da" ili "Ne" vrijednost.', None

    try:
        output['je_poreski_obaveznik'] = validators.boolean(data.get('isTaxpayer'))
    except (Exception, ) as exception:
        # logger.error('Invalid parameter "isTaxpayer"')
        return 'Polje "Je poreski obveznik?" mora biti "Da" ili "Ne" vrijednost.', None

    try:
        output['ziroracun'] = validators.string(data.get('bankAccount'), allow_none=True)
    except (Exception, ) as exception:
        # logger.error('Invalid parameter "bankAccount"')
        return 'Polje "Žiro račun" mora biti tekst.', None

    try:
        output['telefon'] = validators.string(data.get('phoneNumber'), allow_none=True)
    except (Exception, ) as exception:
        # logger.error('Invalid parameter "phoneNumber"')
        return 'Polje "Telefon" mora biti tekst.', None

    try:
        output['email'] = validators.string(data.get('emailAddress'), allow_none=True)
    except (Exception, ) as exception:
        # logger.error('Invalid parameter "emailAddress"')
        return 'Polje "E-mail" mora biti tekst.', None

    return None, output
