import bottle

from backend.podesavanja import podesavanja


def api__soap__wsdl():
    return bottle.static_file(podesavanja.SOAP_API_WSDL, root='schemas', download=True)
