from backend.opb import misc_opb


class ParsingError(Exception):
    pass


def not_empty(value):
    pass


def required(value):
    if value is None:
        raise ParsingError()


def boolean(value, allow_none=False, empty_value: bool = None):
    if value is None:
        if allow_none:
            return value
        else:
            raise ValueError()

    if isinstance(value, str):
        value = value.strip()
        if value in ('True', 'true', '1'):
            return True
        elif value in ('False', 'false', '0'):
            return False
        elif empty_value is not None:
            return empty_value
        else:
            raise ValueError()

    if isinstance(value, int):
        if value == 1:
            return True
        elif value == 0:
            return False
        else:
            raise ValueError()

    if isinstance(value, bool):
        return value

    raise ValueError()


def string(value, allow_none=False, min_length=None, max_length=None):
    """Validate that value is valid string. If value is string it is automatically
    stripped. If stripped value length is 0 it is converted to None.
    """
    if value is None:
        if allow_none:
            return None
        else:
            raise ValueError()

    if not isinstance(value, str):
        raise TypeError()

    value = value.strip()

    if len(value) == 0:
        if allow_none:
            return None
        else:
            raise ValueError()

    if min_length is not None and len(value) < min_length:
        raise ValueError()

    if max_length is not None and len(value) > max_length:
        raise ValueError()

    return value


def company_id_number(value):
    _value = string(value, allow_none=False)
    if len(_value) != 8 and len(_value) != 13:
        raise ValueError()
    return _value


def integer(value, allow_none=False):
    if value is None:
        if allow_none:
            return value
        else:
            raise ValueError()

    if not isinstance(value, int):
        raise TypeError()

    return value


def country(value, allow_none=False):
    if value is None:
        if allow_none:
            return value
        else:
            raise ValueError()

    if not isinstance(value, int):
        raise TypeError()

    output = misc_opb.get_country_by_id(value)
    if output is None:
        raise ValueError()

    return output


def dict_(value, allow_none=False):
    if value is None:
        if allow_none:
            return None
        else:
            raise ValueError()

    if not isinstance(value, dict):
        raise TypeError()

    return value
