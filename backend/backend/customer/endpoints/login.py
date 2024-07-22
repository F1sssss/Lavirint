import bottle
import simplejson as json

from backend.core.schema_validation import validate
from backend.opb import operater_opb
from backend.podesavanja import podesavanja
from backend.serializers import operater_schema


def api__login():
    podaci = validate(bottle.request.json, post_data_schema)

    operater = operater_opb.nadji_operatera_po_pibu_i_mejlu(podaci['pib'], podaci['email'])
    if operater is None:
        return json.dumps({
            'imaGresku': True,
            'opisGreske': 'Kombinacija prijavnih podataka nije ispravna'
        }, **podesavanja.JSON_DUMP_OPTIONS)

    if not operater_opb.provjeri_operatera(operater, podaci['lozinka']):
        return json.dumps({
            'imaGresku': True,
            'opisGreske': 'Kombinacija prijavnih podataka nije ispravna'
        }, **podesavanja.JSON_DUMP_OPTIONS)


    bottle.request.session['operater_id'] = operater.id
    bottle.request.session.save()

    print(bottle.request.session)

    return json.dumps(operater_schema.dump(operater), **podesavanja.JSON_DUMP_OPTIONS)


post_data_schema = {
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'description': 'POST schema za provjeru prijavnih podataka korisnika',
    'type': 'object',
    'properties': {
        'pib': {
            'type': 'string',
            "pattern": "^\\d+$",
            "description": "Unique customer ID."
        },
        'email': {
            'type': 'string'
        },
        'lozinka': {
            'type': 'string',
            "minLength": 4,
            "maxLength": 64
        }
    },
    'required': [
        'pib',
        'email',
        'lozinka'
    ]
}
