import re

tax_period_stype = re.compile(r"^((0[1-9])|(1[0-2]))/(\d{4})$")
identification_type_stype = re.compile(r'^[123456]$')
registration_code_stype = re.compile(r'^[a-z]{2}[0-9]{3}[a-z]{2}[0-9]{3}$')
decimal_neg_stype = re.compile(r'^-?([1-9][0-9]*|0)\.[0-9]{2}|0$')
utc_stype = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([+-][0-9]{2}:[0-9]{2}|Z)$')
decimal_4_stype = re.compile(r'^([1-9][0-9]*|0)\.[0-9]{2,4}|0$')
double_neg_for_quantity_stype = re.compile(r'^-?([1-9][0-9]*|0)(\.[0-9]{1,3})?$')
hex_32_stype = re.compile(r'^[0-9a-fA-F]{32}$')
