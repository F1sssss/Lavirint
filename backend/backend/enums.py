from enum import Enum


class CustomerInvoiceView(Enum):
    REGULAR_INVOICES = 1
    ADVANCE_INVOICES = 2
    CREDIT_NOTES = 3
    REGULAR_INVOICE_TEMPLATES = 4


class OrdinalNumberCounterType(Enum):
    EFI_COUNT = 1
    REGULAR_INVOICES = 2
    ADVANCE_INVOICES = 3
    CREDIT_NOTES = 4
    INVOICE_TEMPLATES = 5
    CALCULATIONS = 6
