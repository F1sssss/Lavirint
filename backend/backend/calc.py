from decimal import ROUND_HALF_UP
from decimal import Decimal


def round_half_up(number, decimals):
    quantize_value = Decimal(1) / (Decimal(10) ** Decimal(decimals))
    return number.quantize(quantize_value, ROUND_HALF_UP)


def format_decimal(number, min_decimals, max_decimals):
    rounded_number = round_half_up(number, max_decimals)

    parts = str(rounded_number).split('.')

    if len(parts) == 1:
        decimals = ''
    else:
        decimals = parts[1].rstrip('0')

    decimals += max(min_decimals - len(decimals), 0) * '0'

    if len(decimals) == 0:
        return parts[0].lstrip().rstrip()
    else:
        return (parts[0] + '.' + decimals[:max_decimals]).lstrip().rstrip()
