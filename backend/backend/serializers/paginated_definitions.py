from marshmallow import Schema
from marshmallow import fields

from backend.serializers.schema_definitions import FakturaSchema


class InvoiceSearchResultSchema(Schema):
    broj_stranice = fields.Integer()
    broj_stavki_po_stranici = fields.Integer()
    stavke = fields.Nested(FakturaSchema, many=True)
    ukupan_broj_stavki = fields.Integer()
