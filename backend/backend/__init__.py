import bottle
from beaker.middleware import SessionMiddleware

from backend.agent.routing import setup_agent_frontend_routes
from backend.customer import setup_customer_frontend_routes
from backend.logging import bottle_logging
from backend.podesavanja import podesavanja
from backend.soap_api.routing import setup_soap_api_routes


def create_app():
    bottle.BaseRequest.MEMFILE_MAX = 2097152  # 2MB

    agent_app: bottle.Bottle = bottle.Bottle()
    agent_app.install(bottle_logging)
    setup_agent_frontend_routes(agent_app)
    agent_middleware = SessionMiddleware(agent_app, {
        'session.cookie_domain': podesavanja.AGENT_COOKIE_DOMAIN,
        'session.samesite': 'Lax',
        'session.type': 'file',
        'session.cookie_expires': 79200,
        'session.data_dir': './agent_sessions',
        'session.auto': True,
        'session.key': 'agent.session.id'
    })

    customer_app: bottle.Bottle = bottle.Bottle()
    customer_app.install(bottle_logging)
    setup_customer_frontend_routes(customer_app)
    customer_app_middleware = SessionMiddleware(customer_app, {
        'session.cookie_domain': podesavanja.CUSTOMER_COOKIE_DOMAIN,
        'session.samesite': 'Lax',
        'session.type': 'file',
        'session.cookie_expires': 79200,
        'session.data_dir': './customer_sessions',
        'session.auto': True,
        'session.key': 'customer.session.id'
    })

    soap_api_app: bottle.Bottle = bottle.Bottle()
    soap_api_app.install(bottle_logging)
    setup_soap_api_routes(soap_api_app)

    def dispatcher(environ, start_response):
        path = environ.get("PATH_INFO", "")
        # if path.startswith("/api/agent"):
        #     return agent_middleware(environ, start_response)

        if path.startswith("/api/soap"):
            return soap_api_app(environ, start_response)
        elif path.startswith("/api/agent"):
            return agent_middleware(environ, start_response)
        elif path.startswith("/api/customer"):
            return customer_app_middleware(environ, start_response)
        else:
            start_response("404 Not Found",  [("Content-type", "text/plain")])
            return [b"404 Not Found"]

    return dispatcher

    # return SessionMiddleware(base_app, {
    #     'session.type': 'database',
    #     'session.url': podesavanja.SQLALCHEMY_DATABASE_URI,
    #     'session.cookie_expires': 79200,
    #     'session.data_dir': './sessions',
    #     'session.auto': True
    # })
