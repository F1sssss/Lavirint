from datetime import datetime
from typing import Optional

from backend.podesavanja import podesavanja


class ParsingError(Exception):
    pass


def has_key_or_raise(data: dict, key: str):
    if key not in data:
        return f'Missing required parameter "{key}".'
    else:
        return None


def get_tax_period(data: any, key: str) -> datetime:
    value = data.get(key)
    if value is None:
        raise ParsingError(f'Missing required parameter "{key}".')

    if not isinstance(value, str):
        raise ParsingError(f'Parameter "{key}" must be string.')

    try:
        r = datetime.fromisoformat(value)
        return r.replace(hour=0, minute=0, second=0, microsecond=0)
    except (Exception, ):
        raise ParsingError(f'Parameter {key} is not valid datetime format.')


def get_datetime(data: any, key: str, optional=False) -> Optional[datetime]:
    value = data.get(key)
    if value is None:
        if not optional:
            raise ParsingError(f'Missing required parameter "{key}".')
        return None

    if not isinstance(value, str):
        raise ParsingError(f'Parameter "{key}" must be string.')

    try:
        return datetime.fromisoformat(value.replace('Z', podesavanja.TIMEZONE))
    except (Exception,):
        raise ParsingError(f'Parameter {key} is not valid datetime format.')


def get_dict(data: any, key: str):
    value = data.get(key)
    if value is None:
        raise ParsingError(f'Missing required parameter "{key}".')

    if not isinstance(value, dict):
        raise ParsingError(f'Parameter "{key}" must be dict.')

    return value


def get_int(data: any, key: str, optional: bool = False):
    value = data.get(key)
    if value is None:
        if not optional:
            raise ParsingError(f'Missing required parameter "{key}".')
        return None

    if not isinstance(value, int):
        raise ParsingError(f'Parameter "{key}" must be dict.')

    return value


def get_string(data: any, key: str):
    value = data.get(key)
    if value is None:
        raise ParsingError(f'Missing required parameter "{key}".')

    if not isinstance(value, str):
        raise ParsingError(f'Parameter "{key}" must be string.')

    return value


def get_bool(data: any, key: str, optional: bool = False):
    value = data.get(key)
    if value is None:
        if not optional:
            raise ParsingError(f'Missing required parameter "{key}".')

    if not isinstance(value, bool):
        raise ParsingError(f'Parameter "{key}" must be boolean.')

    return value
