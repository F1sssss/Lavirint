from abc import abstractmethod

from backend import i18n


class FiscalizationException(Exception):

    @abstractmethod
    def get_message(self, locale: str = i18n.LOCALE_SR_LATN_ME) -> str:
        pass


class CertificateDecryptionInvalidFile(FiscalizationException):
    def get_message(self, locale=i18n.LOCALE_SR_LATN_ME):
        if locale == i18n.LOCALE_SR_LATN_ME:
            return "Došlo je do greške prilikom otvaranja sertifikata. Datoteka nije ispravnog formata."  # noqa E501
        elif locale == i18n.LOCALE_EN_US:
            return "Unable to open certificate. File content is not valid."


class CertificateDecryptionInvalidPassword(FiscalizationException):
    def get_message(self, locale=i18n.LOCALE_SR_LATN_ME):
        if locale == i18n.LOCALE_SR_LATN_ME:
            return "Došlo je do greške prilikom otvaranja sertifikata. Lozinka nije ispravna."  # noqa E501
        elif locale == i18n.LOCALE_EN_US:
            return "Unable to open certificate. Password is incorrect."


class CertificateDecryptionUnknownException(FiscalizationException):
    def get_message(self, locale=i18n.LOCALE_SR_LATN_ME):
        if locale == i18n.LOCALE_SR_LATN_ME:
            return "Došlo je do nepoznate greške prilikom otvaranja sertifikata. Kontaktirajte tehničku podršku."  # noqa E501
        elif locale == i18n.LOCALE_EN_US:
            return "An unknown error occured while opening certificate. Please contact sistem administrators."


class CertificateDecryptionFileNotFoundException(FiscalizationException):
    def get_message(self, locale=i18n.LOCALE_SR_LATN_ME):
        if locale == i18n.LOCALE_SR_LATN_ME:
            return "Došlo je do greške prilikom otvaranja sertifikata. Datoteka nije pronađena."  # noqa E501
        elif locale == i18n.LOCALE_EN_US:
            return "An error occured while opening certificate. Certificate file not found."
