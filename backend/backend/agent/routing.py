from datetime import datetime

import bottle
from bottle import Bottle

from . import endpoints

from backend.db import db
from backend.podesavanja import podesavanja


def setup_agent_frontend_routes(app: Bottle):
    app.route(
        '/api/agent/data-service/load',
        'POST', endpoints.data_service.load.controller)

    app.route(
        '/api/agent/login-view/submit',
        'POST', endpoints.login_view.submit.controller)

    app.route(
        '/api/agent/customer-insert-view/submit',
        'POST', endpoints.customer_insert_view.submit.controller)

    app.route(
        '/api/agent/customer-update-view/load',
        'POST', endpoints.customer_update_view.load.controller)
    app.route(
        '/api/agent/customer-update-view/submit',
        'POST', endpoints.customer_update_view.submit.controller)

    app.route(
        '/api/agent/customer-list-view/load',
        'POST', endpoints.customer_list_view.load.controller)
    app.route(
        '/api/agent/customer-list-view/update_active_status',
        'POST', endpoints.customer_list_view.update_active_status.controller)
    app.route(
        '/api/agent/customer-list-view/update_taxpayer_status',
        'POST', endpoints.customer_list_view.update_taxpayer_status.controller)

    app.route(
        '/api/agent/customer-certificates-view/load',
        'POST', endpoints.customer_certificates_view.load.controller)
    app.route(
        '/api/agent/customer-certificates-view/delete',
        'POST', endpoints.customer_certificates_view.delete.controller)
    app.route(
        '/api/agent/customer-certificates-view/download',
        'POST', endpoints.customer_certificates_view.download.controller)

    app.route(
        '/api/agent/customer-certificate-upload-view/load',
        'POST', endpoints.customer_certificate_upload_view.load.controller)
    app.route(
        '/api/agent/customer-certificate-upload-view/submit',
        'POST', endpoints.customer_certificate_upload_view.submit.controller)

    app.route(
        '/api/agent/customer-business-units-view/load',
        'POST', endpoints.customer_business_units_view.load.controller
    )

    app.add_hook('before_request', before_request)
    app.add_hook('after_request', after_request)

    app.route('', 'OPTIONS', http_method_options_handler)
    app.route('<path:path>', 'OPTIONS', http_method_options_handler)


def before_request():
    bottle.request.datetime = datetime.now()
    bottle.request.session = bottle.request.environ['beaker.session']


def after_request():
    db.session.close()

    for header, value in podesavanja.AGENT_HTTP_RESPONSE_HEADERS.items():
        bottle.response.set_header(header, value)


def http_method_options_handler(path=None):
    return
