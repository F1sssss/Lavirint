from datetime import datetime

import bottle
import pytz
import simplejson as json

from backend.core.schema_validation import validate
from backend.customer.auth import requires_authentication
from backend.models import KnjiznoOdobrenjeStavka
from backend.opb import credit_note_opb
from backend.serializers import knjizno_odobrenje__processing_schema


@requires_authentication
def views__credit_note_create__on_fiscalize(operater, firma):
    podaci = bottle.request.json.copy()
    fiscalization_date = datetime.now(pytz.timezone('Europe/Podgorica'))

    data = validate(podaci, post_credit_note_create_schema)

    processing, credit_note = credit_note_opb.make_credit_note(
        firma, operater, operater.naplatni_uredjaj, data, fiscalization_date)

    return json.dumps(knjizno_odobrenje__processing_schema.dump({
        'is_success': processing.is_success,
        'credit_note': credit_note
    }))


post_credit_note_create_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "POST credit note schema",
    "type": "object",
    "properties": {
        "komitent_id": {
            "type": "integer",
            "minimum": 1
        },
        "valuta_id": {
            "type": "integer",
            "minimum": 1
        },
        "tax_amount": {
            "type": "number"
        },
        "return_amount": {
            "type": "number"
        },
        "return_amount_with_tax": {
            "type": "number"
        },
        "discount_amount": {
            "type": "number"
        },
        "discount_amount_with_tax": {
            "type": "number"
        },
        "return_and_discount_amount": {
            "type": "number",
            "exclusiveMinimum": 0
        },
        "grupe_poreza": {
            "type": "array",
            "minContains": 1,
            "items": {
                "type": "object",
                "properties": {
                    "tax_rate": {
                        "type": "integer",
                        "enum": [0, 7, 21]
                    },
                    "tax_amount": {
                        "type": "number"
                    },
                    "return_amount": {
                        "type": "number"
                    },
                    "return_amount_with_tax": {
                        "type": "number"
                    },
                    "discount_amount": {
                        "type": "number"
                    },
                    "discount_amount_with_tax": {
                        "type": "number"
                    },
                    "return_and_discount_amount": {
                        "type": "number",
                        "exclusiveMinimum": 0
                    },
                    "return_and_discount_amount_with_tax": {
                        "type": "number",
                        "exclusiveMinimum": 0
                    }
                }
            }
        },
        "fakture_ids": {
            "type": "array",
            "items": {
                "type": "integer",
                "minimum": 0
            }
        },
        "stavke": {
            "type": "array",
            "items": {
                "allOf": [
                    {
                        "if": {
                            "properties": {
                                "tax_rate": {"enum": [7, 21]}
                            }
                        },
                        "then": {
                            "properties": {
                                "tax_amount": {"exclusiveMinimum": 0}
                            }
                        },
                        "else": {
                            "properties": {
                                "tax_amount": {"const": 0}
                            }
                        }
                    },
                    {
                        "if": {
                            "properties": {
                                "type": {"const": 1}
                            },
                            "required": ["type"]
                        },
                        "then": {
                            "properties": {
                                "discount_amount": {"const": 0},
                                "discount_amount_with_tax": {"const": 0},
                                "return_amount": {"exclusiveMinimum": 0},
                                "return_amount_with_tax": {"exclusiveMinimum": 0}
                            }
                        }
                    },
                    {
                        "if": {
                            "properties": {
                                "type": {"const": 2}
                            },
                            "required": ["type"]
                        },
                        "then": {
                            "properties": {
                                "return_amount": {"const": 0},
                                "return_amount_with_tax": {"const": 0},
                                "discount_amount": {"exclusiveMinimum": 0},
                                "discount_amount_with_tax": {"exclusiveMinimum": 0}
                            }
                        }
                    }
                ],
                "properties": {
                    "description": {
                        "type": "string",
                        "minLength": 0,
                        "maxLength": 255
                    },
                    "type": {
                        "type": "integer",
                        "enum": [KnjiznoOdobrenjeStavka.ITEM_TYPE_RETURN, KnjiznoOdobrenjeStavka.ITEM_TYPE_DISCOUNT]
                    },
                    "tax_rate": {
                        "type": "integer",
                        "enum": [0, 7, 21]
                    },
                    "tax_amount": {
                        "type": "number"
                    },
                    "return_amount": {
                        "type": "number"
                    },
                    "return_amount_with_tax": {
                        "type": "number"
                    },
                    "discount_amount": {
                        "type": "number"
                    },
                    "discount_amount_with_tax": {
                        "type": "number"
                    }
                }
            }
        }
    }
}