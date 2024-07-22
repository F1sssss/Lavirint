import simplejson as json
from datetime import datetime, timedelta

import bottle

from backend.podesavanja import podesavanja
from backend.customer.auth import requires_authentication
from backend.opb import report_opb, faktura_opb


@requires_authentication
def views__izvjestaj_po_artiklima_forma__on_submit(operater, firma):
    data = bottle.request.json.copy()

    now = datetime.now()
    param_datum_od = datetime.strptime(data['start'], "%Y-%m-%dT%H:%M:%S.%fZ")
    param_datum_do = datetime.strptime(data['end'], "%Y-%m-%dT%H:%M:%S.%fZ")
    param_datum_do = (param_datum_do + timedelta(seconds=1)).replace(microsecond=0)

    buyer_id = data.get('buyerId')
    buyer = None
    if buyer_id is not None:
        buyer = faktura_opb.get_buyer_by_id(firma, buyer_id)
        if buyer is None:
            bottle.response.status = 400
            return bottle.response

    report_items = report_opb.izvjestaj_po_artiklima(operater.naplatni_uredjaj_id, param_datum_od, param_datum_do, buyer)

    response_data = {}
    response_data['start'] = param_datum_od.isoformat()
    response_data['end'] = (param_datum_do - timedelta(seconds=1, microseconds=0)).isoformat()
    response_data['document_datetime'] = now.isoformat()
    response_data['operator_efi_code'] = operater.kodoperatera
    response_data['items'] = []
    response_data['buyer'] = None
    if buyer is not None:
        response_data['buyer'] = {
            'name': buyer.naziv
        }

    for item in report_items:
        item_data = {}
        item_data['item_template'] = {}
        item_data['total_price'] = item.ukupna_cijena_prodajna
        item_data['quantity'] = item.kolicina
        item_data['item_template_description'] = item.artikal_naziv

        response_data['items'].append(item_data)

    return json.dumps(
        response_data,
        **podesavanja.JSON_DUMP_OPTIONS
    )