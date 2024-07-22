import decimal
import re
from contextlib import contextmanager
from datetime import datetime
from typing import Tuple
from typing import Union

from backend import i18n
from backend import patterns


class Errors:
    MISSING_MANDATORY_VALUE = {
        i18n.LOCALE_SR_LATN_ME: 'Nedostaje obavezan podatak.',
        i18n.LOCALE_EN_US: 'Mandatory information is missing.'
    }

    INVALID_DECIMAL_VALUE = {
        i18n.LOCALE_SR_LATN_ME: 'Vrijednost "%s" nije ispravnog formata. Mora biti cio broj.',
        i18n.LOCALE_EN_US: 'Unable to parse value "%s" as decimal.'
    }

    ERROR_BAD_DATETIME_FORMAT = {
        i18n.LOCALE_SR_LATN_ME:
            'Vrijednost "%s" nije ispravnog formata. Očekivani format: %%Y-%%m-%%d %%H:%%M:%%S'
            'Primjer: 2021-01-01 00:00:00',
        i18n.LOCALE_EN_US:
            'Unable to parse value "%s" as datetime. Expected format: %%Y-%%m-%%d %%H:%%M:%%S. '
            'Example: 2021-01-01 00:00:00.'
    }


class Fields:
    INVOICE_SELLER_IDENTIFICATION = 'invoice_seller_identification'
    INVOICE_TYPE = 'invoice_type'
    INVOICE_DATE_CREATED = 'invoice_date_created'
    INVOICE_TOTAL_BASE_PRICE = 'invoice_total_base_price'
    INVOICE_TOTAL_BASE_PRICE_WITH_REBATE_ONLY = 'invoice_total_base_price_with_rebate_only'
    INVOICE_TOTAL_BASE_PRICE_WITH_TAX_ONLY = 'invoice_total_base_price_with_tax_only'
    INVOICE_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX = 'invoice_total_base_price_with_rebate_and_tax'
    INVOICE_TAX_AMOUNT = 'invoice_tax_amount'
    INVOICE_REBATE_AMOUNT_BEFORE_VAT = 'invoice_rebate_amount_before_vat'
    INVOICE_REBATE_AMOUNT_AFTER_VAT = 'invoice_rebate_amount_after_vat'
    INVOICE_OPERATOR_EFI_CODE = 'invoice_operator_efi_code'
    INVOICE_TCR_CODE = 'invoice_tcr_code'
    INVOICE_VALUE_DATE = 'invoice_value_date'
    INVOICE_CORRECTION_INVOICE_IIC_REFERENCE = 'invoice_correction_invoice_iic_reference'
    INVOICE_TAX_PERIOD = 'invoice_tax_period'
    INVOICE_PAYMENT_TYPE_ID = 'invoice_payment_type_id'
    INVOICE_CURRENCY_ISO_CODE = 'invoice_currency_iso_code'
    INVOICE_CURRENCT_EXCHANGE_RATE = 'invoice_currenct_exchange_rate'
    INVOICE_NUMBER_OF_INVOICE_ITEMS = 'invoice_number_of_invoice_items'
    INVOICE_NUMBER_OF_TAX_ITEMS = 'invoice_number_of_tax_items'
    INVOICE_HAS_BUYER = 'invoice_has_buyer'
    INVOICE_NOTE = 'invoice_note'

    INVOICE_TYPE_OF_SELFISS = 'invoice_type_of_selfiss'  # TODO: deprecated
    INVOICE_IS_SIMPLIFIED_INV = 'invoice_is_simplified_inv'  # TODO: deprecated

    BUYER_IDENTIFICATION_TYPE_ID = 'buyer_identification_type_id'
    BUYER_IDENTIFICATION_NUMBER = 'buyer_identification_number'
    BUYER_NAME = 'buyer_name'
    BUYER_ADRESS = 'buyer_adress'
    BUYER_CITY = 'buyer_city'
    BUYER_COUNTRY_CODE = 'buyer_country_code'

    ITEM_DESCRIPTION = 'item_description'
    ITEM_CODE = 'item_code'
    ITEM_UNIT_OF_MEASURE = 'item_unit_of_measure'
    ITEM_QUANTITY = 'item_quantity'
    ITEM_UNIT_BASE_PRICE = 'item_unit_base_price'
    ITEM_REBATE_PERCENTAGE = 'item_rebate_percentage'
    ITEM_UNIT_BASE_PRICE_WITH_REBATE_ONLY = 'item_unit_base_price_with_rebate_only'
    ITEM_UNIT_BASE_PRICE_WITH_TAX_ONLY = 'item_unit_base_price_with_tax_only'
    ITEM_UNIT_BASE_PRICE_WITH_REBATE_AND_TAX = 'item_unit_base_price_with_rebate_and_tax'
    ITEM_TOTAL_BASE_PRICE = 'item_total_base_price'
    ITEM_TOTAL_BASE_PRICE_WITH_REBATE_ONLY = 'item_total_base_price_with_rebate_only'
    ITEM_TOTAL_BASE_PRICE_WITH_TAX_ONLY = 'item_total_base_price_with_tax_only'
    ITEM_TOTAL_BASE_PRICE_WITH_REBATE_AND_TAX = 'item_total_base_price_with_rebate_and_tax'
    ITEM_TAX_PERCENTAGE = 'item_tax_percentage'
    ITEM_VAT_EXEMPTION_REASON_ID = 'item_vat_exemption_reason_id'
    ITEM_TOTAL_TAX_AMOUNT = 'item_total_tax_amount'
    ITEM_TOTAL_REBATE_AMOUNT_BEFORE_VAT = 'item_total_rebate_amount_before_vat'
    ITEM_TOTAL_REBATE_AMOUNT_AFTER_VAT = 'item_total_rebate_amount_after_vat'

    TAX_GROUP_NUMBER_OF_MATCHED_INVOICE_ITEMS = 'tax_group_number_of_matched_invoice_items'
    TAX_GROUP_BASE_PRICE = 'tax_group_base_price'
    TAX_GROUP_BASE_PRICE_WITH_REBATE = 'tax_group_base_price_with_rebate'
    TAX_GROUP_BASE_PRICE_WITH_TAX = 'tax_group_base_price_with_tax'
    TAX_GROUP_BASE_PRICE_WITH_REBATE_AND_TAX = 'tax_group_base_price_with_rebate_and_tax'
    TAX_GROUP_TAX_PERCENTAGE = 'tax_group_tax_percentage'
    TAX_GROUP_TAX_AMOUNT = 'tax_group_tax_amount'
    TAX_GROUP_REBATE_AMOUNT_BEFORE_VAT = 'tax_group_rebate_amount_before_vat'
    TAX_GROUP_REBATE_AMOUNT_AFTER_VAT = 'tax_group_rebate_amount_after_vat'


class ParseException(Exception):
    def __init__(self, error_messages: dict = None, extra: dict = None):
        super().__init__(error_messages)

        self.error_messages = error_messages
        self.extra = extra


def to_registration_code(value: str) -> str:
    if patterns.registration_code_stype.search(value) is None:
        raise ParseException({
            i18n.LOCALE_SR_LATN_ME: 'Unable to parse value "%s" as registration code. Pattern check failed.' % value,
            i18n.LOCALE_EN_US: 'Unable to parse value "%s" as registration code. Pattern check failed.' % value
        })

    return value


def to_tax_period(value: str) -> str:
    if patterns.tax_period_stype.search(value) is None:
        raise ParseException({
            i18n.LOCALE_SR_LATN_ME: 'Unable to parse value "%s" as tax period. Pattern check failed.' % value,
            i18n.LOCALE_EN_US: 'Unable to parse value "%s" as tax period. Pattern check failed.' % value
        })

    _parts = value.split('/')
    _value = datetime.now()
    _value = _value.replace(month=int(_parts[0]), year=int(_parts[1]), day=1, hour=0, minute=0, second=0, microsecond=0)

    return _value.isoformat()


def to_string_or_none(value: str, none_values: Tuple = ('', None,), strip: bool = True) -> Union[str, None]:
    _value = value

    if strip:
        _value = _value.strip()

    if value in none_values:
        return None

    return _value


def raise_if(should_raise: bool, error_message: [list] = None, locale=i18n.DEFAULT_LOCALE):
    if isinstance(error_message, str):
        error_message = [error_message]

    if should_raise:
        raise ParseException(error_message.get(locale) or 'Unable to parse value "%s".')


def raise_if_not_pattern(value: str, pattern: re.Pattern):
    if pattern.search(value) is None:
        raise ParseException({
            i18n.LOCALE_SR_LATN_ME: 'Unable to parse value "%s". Pattern check failed.',  # TODO
            i18n.LOCALE_EN_US: 'Unable to parse value "%s". Pattern check failed.'
        })

    return value


def to_boolean(value: str, true_values: tuple = ('1', 'true'), false_values: tuple = ('0', 'false')) -> bool:
    if value in true_values:
        return True
    elif value in false_values:
        return False
    else:
        raise ParseException({
            i18n.LOCALE_SR_LATN_ME:
                'Unable to parse value "%s" as boolean. Correct values are "0", "1", "true", "false".',  # TODO
            i18n.LOCALE_EN_US:
                'Unable to parse value "%s" as boolean. Correct values are "0", "1", "true", "false".'
        })


def to_integer(value: str) -> int:
    try:
        return int(value)
    except Exception:
        raise ParseException({
            i18n.LOCALE_SR_LATN_ME: 'Unable to parse value "%s" as integer' % value,  # TODO
            i18n.LOCALE_EN_US: 'Unable to parse value "%s" as integer' % value
        })


def to_datetime(value: str, format_='%Y-%m-%d %H:%M:%S') -> str:
    try:
        return datetime.strptime(value, format_).isoformat()
    except Exception:
        raise ParseException({k: v % value for k, v in Errors.ERROR_BAD_DATETIME_FORMAT.copy()})


def to_decimal(value: str) -> decimal.Decimal:
    try:
        return decimal.Decimal(value)
    except Exception:
        raise ParseException(Errors.INVALID_DECIMAL_VALUE)


class Parser:

    def __init__(self, expected_headers):
        self.expected_headers = expected_headers
        self.expected_headers_length = len(expected_headers)

        self.headers = None
        self.headers_line_number = None

        self.values = None
        self.values_line_number = None
        self.values_length = None

        self.record = None

    def set_headers(self, headers, line_number, check_length=True):
        self.headers = headers
        self.headers_line_number = line_number

        if check_length == self.headers != self.expected_headers:
            raise ParseException(
                error_messages={
                    i18n.LOCALE_SR_LATN_ME: '',
                    i18n.LOCALE_EN_US: 'Invalid header values.'
                },
                extra={
                    'line_number': self.headers_line_number
                }
            )

    def set_values(self, values, line_number, check_length=True):
        self.values = values
        self.values_line_number = line_number
        self.values_length = len(self.values)

        if check_length and self.values_length != self.expected_headers_length:
            raise ParseException(
                error_messages={
                    i18n.LOCALE_SR_LATN_ME:
                        'Dužina reda nije ispravna. Očekivana dužina %s, stvarna dužina %s.'
                        % (self.expected_headers_length, self.values_length),
                    i18n.LOCALE_EN_US:
                        'Invalid record length. Expected %s, got %s values.'
                        % (self.expected_headers_length, self.values_length)
                },
                extra={
                    'line_number': self.values_line_number
                }
            )

    def refresh_record(self):
        self.record = dict(zip(self.headers, self.values))

    def set_record(self, headers, headers_line_number, values, values_line_number):
        self.set_headers(headers, headers_line_number)
        self.set_values(values, values_line_number)

    @contextmanager
    def get_field(self, field_name):
        try:
            if field_name not in self.headers:
                raise ParseException(
                    error_messages={
                        i18n.LOCALE_SR_LATN_ME: f'Polje "{field_name}" ne postoji u listi očekivanih zaglavlja.',
                        i18n.LOCALE_EN_US: f'Field "{field_name}" does not exist in expected headers\' list.'
                    },
                    extra={
                        'line_number': self.values_line_number
                    }
                )

            yield self.record.get(field_name)
        except ParseException as exception:
            exception.extra = {
                'line_number': self.values_line_number,
                'field_name': field_name,
                'field_index': self.headers.index(field_name)
            }
            raise
