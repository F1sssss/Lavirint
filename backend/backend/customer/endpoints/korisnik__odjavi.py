import bottle

from backend.customer.auth import requires_authentication


@requires_authentication
def api__korisnik__odjavi(operater, firma):
    del bottle.request.session['operater_id']
    return bottle.redirect('/')
