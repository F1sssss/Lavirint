from datetime import datetime

import bottle
from bottle import Bottle

from . import endpoints
from . import v2
from backend.db import db
from backend.podesavanja import podesavanja


def setup_customer_frontend_routes(app: Bottle):
    app.route(
        '/api/customer/certificate-upload-modal/submit',
        method='POST',
        callback=v2.certificate_upload_modal.submit.controller
    )
    app.route(
        '/api/customer/certificates-list-view/load',
        method='POST',
        callback=v2.certificates_list_view.load.controller
    )
    app.route(
        '/api/customer/certificates-list-view/delete',
        method='POST',
        callback=v2.certificates_list_view.delete.controller
    )
    app.route(
        path='/api/customer/frontend/initial',
        method='GET',
        callback=endpoints.api__frontend__initial)
    app.route(
        path='/api/customer/credit_note/<credit_note_id>/document',
        method='GET',
        callback=endpoints.api__credit_note__param_credit_note_id__document)
    app.route(
        path='/api/customer/login',
        method='POST',
        callback=endpoints.api__login)
    app.route(
        path='/api/customer/korisnik/listaj',
        method='GET',
        callback=endpoints.api__korisnik__listaj)
    app.route(
        path='/api/customer/korisnik/odjavi',
        method='GET',
        callback=endpoints.api__korisnik__odjavi)
    app.route(
        path='/api/customer/korisnik/izmijeni',
        method='POST',
        callback=endpoints.api__korisnik__izmijeni)
    app.route(
        path='/api/customer/komitent/dodaj',
        method='POST',
        callback=endpoints.api__komitent__dodaj)
    app.route(
        path='/api/customer/komitent/listaj',
        method='GET',
        callback=endpoints.api__komitent__listaj)
    app.route(
        path='/api/customer/komitent/<param_komitent_id>/izmijeni',
        method='POST',
        callback=endpoints.api__komitent__param_komitent_id__izmijeni)
    app.route(
        path='/api/customer/komitent/<param_komitent_id>/listaj',
        method='GET',
        callback=endpoints.api__komitent__param_komitent_id__listaj)
    app.route(
        path='/api/customer/komitent/placanje/dodaj_bulk',
        method='POST',
        callback=endpoints.api__komitent__placanje__dodaj_bulk)
    app.route(
        path='/api/customer/stanje/listaj',
        method='GET',
        callback=endpoints.api__stanje__listaj)
    app.route(
        path='/api/customer/faktura/listaj',
        method='GET',
        callback=endpoints.api__faktura__listaj)
    app.route(
        path='/api/customer/faktura/dodaj',
        method='POST',
        callback=endpoints.api__faktura__dodaj)
    app.route(
        path='/api/customer/faktura/<param_faktura_id>/stampa/<param_tip_stampe>',
        method='GET',
        callback=endpoints.api__faktura__param_faktura_id__stampa__param_tip_stampe)
    app.route(
        path='/api/customer/faktura/<param_faktura_id>/dokument/upload',
        method='POST',
        callback=endpoints.api__faktura__param_faktura_id__dokument__upload)
    app.route(
        path='/api/customer/faktura/<param_faktura_id>/dokument/listaj',
        method='GET',
        callback=endpoints.api__faktura__param_faktura_id__dokument__listaj)
    app.route(
        path='/api/customer/faktura/<param_faktura_id>/storniraj',
        method='POST',
        callback=endpoints.api__faktura__param_faktura_id__storniraj)
    app.route(
        path='/api/customer/faktura/<param_faktura_id>/koriguj',
        method='POST',
        callback=endpoints.api__faktura__param_faktura_id__koriguj)
    app.route(
        path='/api/customer/faktura/<param_faktura_id>/listaj',
        method='GET',
        callback=endpoints.api__faktura__param_faktura_id__listaj)
    app.route(
        path='/api/customer/faktura/<param_invoice_id>/invoice_schedule/add',
        method='POST',
        callback=endpoints.api__faktura__param_invoice_id__invoice_schedule__add)
    app.route(
        path='/api/customer/faktura/<param_invoice_id>/invoice_schedule/deactivate',
        method='POST',
        callback=endpoints.api__faktura__param_invoice_id__invoice_schedule__deactivate)
    app.route(
        path='/api/customer/faktura/<param_faktura_id>/mail',
        method='POST',
        callback=endpoints.api__faktura__param_faktura_id__mail)
    app.route(
        path='/api/customer/advance/create',
        method='POST',
        callback=endpoints.advance__create)
    app.route(
        path='/api/customer/final_invoice/create',
        method='POST',
        callback=endpoints.api__final_invoice__create)
    app.route(
        path='/api/customer/profaktura/dodaj',
        method='POST',
        callback=endpoints.api__profaktura__dodaj)
    app.route(
        path='/api/customer/profaktura/listaj',
        method='GET',
        callback=endpoints.api__profaktura__listaj)
    app.route(
        path='/api/customer/profaktura/<param_profaktura_id>/listaj',
        method='GET',
        callback=endpoints.api__profaktura__param_profaktura_id__listaj)
    app.route(
        path='/api/customer/izvjestaj/zurnal/<param_datum_od>/<param_datum_do>',
        method='GET',
        callback=endpoints.api__izvjestaj__zurnal__param_datum_od__param_datum_do)
    app.route(
        path='/api/customer/izvjestaj/presjek_stanja',
        method='GET',
        callback=endpoints.api__izvjestaj__presjek_stanja)
    app.route(
        path='/api/customer/izvjestaj/dnevni/<param_datum>',
        method='GET',
        callback=endpoints.api__izvjestaj__dnevni__param_datum)
    app.route(
        path='/api/customer/izvjestaj/periodicni/<param_datum_od>/<param_datum_do>',
        method='GET',
        callback=endpoints.api__izvjestaj__periodicni__param_datum_od__param_datum_do)
    app.route(
        path='/api/customer/frontend/invoice/regular/all',
        method='GET',
        callback=endpoints.api__frontend__invoice__regular__all)
    app.route(
        path='/api/customer/frontend/invoice/create/type1',
        method='GET',
        callback=endpoints.api__frontend__invoice__create__type1)
    app.route(
        path='/api/customer/frontend/final_invoice/create',
        method='GET',
        callback=endpoints.api__frontend__final_invoice__create)
    app.route(
        path='/api/customer/frontend/invoice/advance/all',
        method='GET',
        callback=endpoints.api__frontend__invoice__advance__all)
    app.route(
        path='/api/customer/frontend/invoice/template/all',
        method='GET',
        callback=endpoints.api__frontend__invoice__template__all)
    app.route(
        path='/api/customer/frontend/buyer/<param_buyer_id>/state',
        method='GET',
        callback=endpoints.api__frontend__buyer__param_buyer_id__state)
    app.route(
        path='/api/customer/firma/dospjela_faktura/listaj',
        method='GET',
        callback=endpoints.api__firma__dospjela_faktura__listaj)
    app.route(
        path='/api/customer/firma/dospjela_faktura/notifikacija/listaj',
        method='GET',
        callback=endpoints.api__firma__dospjela_faktura__notifikacija__listaj)
    app.route(  # Deprecated
        path='/api/customer/modal/invoice_filter',
        method='GET',
        callback=endpoints.api__modal__invoice_filter)
    app.route(
        path='/api/customer/frontend/artikal/unos',
        method='GET',
        callback=endpoints.api__frontend__artikal__unos)
    app.route(
        path='/api/customer/frontend/artikal/<param_artikal_id>/izmijeni',
        method='GET',
        callback=endpoints.api__frontend__artikal__param_artikal_id__izmijeni)
    app.route(
        path='/api/customer/frontend/deposit',
        method='GET',
        callback=endpoints.api__frontend__deposit)
    app.route(
        path='/api/customer/komitent/placanje/<param_placanje_id>/obrisi',
        method='DELETE',
        callback=endpoints.api__komitent__placanje__param_placanje_id__obrisi)
    app.route(
        path='/api/customer/depozit/polozi',
        method='POST',
        callback=endpoints.api__depozit__polozi)
    app.route(
        path='/api/customer/depozit/podigni',
        method='POST',
        callback=endpoints.api__depozit__podigni)
    app.route(
        path='/api/customer/artikal/listaj',
        method='GET',
        callback=endpoints.api__artikal__listaj)
    app.route(
        path='/api/customer/artikal/<param_artikal_id>/listaj',
        method='GET',
        callback=endpoints.api__artikal__param_artikal_id__listaj)
    app.route(
        path='/api/customer/artikal/dodaj',
        method='POST',
        callback=endpoints.api__artikal__dodaj)
    app.route(
        path='/api/customer/artikal/<param_artikal_id>/izmijeni',
        method='POST',
        callback=endpoints.api__artikal__param_artikal_id__izmijeni)
    app.route(
        path='/api/customer/artikal/<param_artikal_id>/obrisi',
        method='POST',
        callback=endpoints.api__artikal__param_artikal_id__obrisi)
    app.route(
        path='/api/customer/artikal/trazi',
        method='POST',
        callback=endpoints.api__artikal__trazi)
    app.route(
        path='/api/customer/grupa_artikala/listaj',
        method='GET',
        callback=endpoints.api__grupa_artikala__listaj)
    app.route(
        path='/api/customer/grupa_artikala/<param_grupa_artikala_id>/listaj',
        method='GET',
        callback=endpoints.api__grupa_artikala__param_grupa_artikala_id__listaj)
    app.route(
        path='/api/customer/grupa_artikala/dodaj',
        method='POST',
        callback=endpoints.api__grupa_artikala__dodaj)
    app.route(
        path='/api/customer/grupa_artikala/<param_grupa_artikala_id>/izmijeni',
        method='POST',
        callback=endpoints.api__grupa_artikala__param_grupa_artikala_id__izmijeni)
    app.route(
        path='/api/customer/drzava/listaj',
        method='GET',
        callback=endpoints.api__drzava__listaj)
    app.route(
        path='/api/customer/vrsta_placanja/listaj',
        method='GET',
        callback=endpoints.api__vrsta_placanja__listaj)
    app.route(
        path='/api/customer/poreska_stopa/listaj',
        method='GET',
        callback=endpoints.api__poreska_stopa__listaj)
    app.route(
        path='/api/customer/jedinica_mjere/listaj',
        method='GET',
        callback=endpoints.api__jedinica_mjere__listaj)
    app.route(
        path='/api/customer/tip_identifikacione_oznake/listaj',
        method='GET',
        callback=endpoints.api__tip_identifikacione_oznake__listaj)
    app.route(
        path='/api/customer/magacin/listaj',
        method='GET',
        callback=endpoints.api__magacin__listaj)
    app.route(
        path='/api/customer/magacin/<param_magacin_id:int>/lager/listaj',
        method='GET',
        callback=endpoints.api__magacin__param_magacin_id__lager__listaj)
    app.route(
        path='/api/customer/kalkulacija/listaj',
        method='GET',
        callback=endpoints.api__kalkulacija__listaj)
    app.route(
        path='/api/customer/kalkulacija/dodaj',
        method='POST',
        callback=endpoints.api__kalkulacija__dodaj)
    app.route(
        path='/api/customer/izvjestaj/po-artiklima/<param_datum_od>/<param_datum_do>',
        method='GET',
        callback=endpoints.api__izvjestaj__po_artiklima__param_datum_od__param_datum_do)
    app.route(
        path='/api/customer/izvjestaj/po-grupama-artikala/<param_datum_od>/<param_datum_do>',
        method='GET',
        callback=endpoints.api__izvjestaj_po__grupama_artikala__param_datum_od__param_datum_do)
    app.route(
        path='/api/customer/on_transition_finish_check_due_payments/turn_off_notifications',
        method='POST',
        callback=endpoints.on_transition_finish_check_due_payments__turn_off_notifications)
    app.route(
        path='/api/customer/firma/listaj',
        method='GET',
        callback=endpoints.api__firma__listaj)
    app.route(
        path='/api/customer/firma/logo/izmijeni',
        method='POST',
        callback=endpoints.api__firma__logo__izmijeni)
    app.route(
        path='/api/customer/firma/izmijeni',
        method='POST',
        callback=endpoints.api__firma__izmijeni)
    app.route(
        path='/api/customer/firma/datoteka/<param_filename>',
        method='GET',
        callback=endpoints.api__firma__datoteka__param_filename)
    app.route(
        path='/api/customer/firma/grupa_artikala/listaj',
        method='GET',
        callback=endpoints.api__firma__grupa_artikala__listaj)
    app.route(
        path='/api/customer/firma/grupa_artikala/<param_grupa_artikala_id>/zaliha/listaj',
        method='GET',
        callback=endpoints.api__firma__grupa_artikala__param_grupa_artikala_id__zaliha__listaj)
    app.route(
        path='/api/customer/firma/podesavanja/smtp/izmijeni',
        method='POST',
        callback=endpoints.api__firma__podesavanja__smtp__izmijeni)
    app.route(
        path='/api/customer/firma/dospjela_faktura/<param_dospjela_faktura_id>/dokument/listaj',
        method='GET',
        callback=endpoints.api__firma__dospjela_faktura__param_dospjela_faktura_id__dokument__listaj)
    app.route(
        path='/api/customer/organizaciona_jedinica/<param_organizaciona_jedinica_id:int>/izmijeni',
        method='POST',
        callback=endpoints.api__organizaciona_jedinica__param_organizaciona_jedinica_id__izmijeni)
    app.route(
        path='/api/customer/smjena/otvori',
        method='POST',
        callback=endpoints.api__smjena__otvori)
    app.route(
        path='/api/customer/smjena/zatvori',
        method='POST',
        callback=endpoints.api__smjena__zatvori)
    app.route(
        path='/mail/test',
        method='POST',
        callback=endpoints.api__mail__test)
    app.route(
        path='/',
        method='OPTIONS',
        callback=http_method_options_handler)
    app.route(
        path='/<path:path>',
        method='OPTIONS',
        callback=http_method_options_handler)

    # ------------------------------------------------------------------------------------------------------------------
    # Version 3.0
    # ------------------------------------------------------------------------------------------------------------------
    app.route(
        path='/api/customer/directives/credit_note_typeahead/on_typeahead_input_change',
        method='POST',
        callback=endpoints.directives__credit_note_typeahead__on_typeahead_input_change)

    app.route(
        path='/api/customer/views/credit_note_create/on_buyer_typeahead_select',
        method='POST',
        callback=endpoints.views__credit_note_create__on_buyer_typeahead_select)
    app.route(
        path='/api/customer/views/credit_note_create/on_fiscalize',
        method='POST',
        callback=endpoints.views__credit_note_create__on_fiscalize)
    app.route(
        path='/api/customer/views/credit_note_create/on_invoice_page_change',
        method='POST',
        callback=endpoints.views__credit_note_create__on_invoice_page_change)
    app.route(
        path='/api/customer/views/credit_note_create/on_load',
        method='POST',
        callback=endpoints.views__credit_note_create__on_load)
    app.route(
        path='/api/customer/views/credit_note_view/on_load',
        method='POST',
        callback=endpoints.views__credit_note_view__on_load
    )
    app.route(
        path='/api/customer/views/faktura_slobodan_unos_korekcije/fiskalizuj',
        method='POST',
        callback=endpoints.views__faktura_slobodan_unos_korekcije__fiskalizuj)
    app.route(
        path='/api/customer/views/izvjestaj_po_artiklima_forma/on_submit',
        method='POST',
        callback=endpoints.views__izvjestaj_po_artiklima_forma__on_submit)
    app.route(
        path='/api/customer/views/komitent_pregled_lista/on_load',
        method='POST',
        callback=endpoints.views__komitent_pregled_lista__on_load)

    app.add_hook('before_request', before_request)
    app.add_hook('after_request', after_request)

    app.error_handler = {
        400: http_response_400_handler
    }


def before_request():
    bottle.request.datetime = datetime.now()
    bottle.request.session = bottle.request.environ['beaker.session']


def after_request():
    db.session.close()

    for header, value in podesavanja.CUSTOMER_HTTP_RESPONSE_HEADERS.items():
        bottle.response.set_header(header, value)


def http_response_400_handler(error):
    return error


def http_method_options_handler(path=None):
    return