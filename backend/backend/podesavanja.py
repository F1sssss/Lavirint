import os


class OsnovaPodesavanja(object):
    CLIENT_CERTIFICATE_STORE = os.environ.get('CLIENT_CERTIFICATE_STORE')
    COMPANY_FILESTORE_PATH = os.environ.get('COMPANY_FILESTORE_PATH')
    DECIMAL_PRECISION = 4

    EFI_FILES_STORE = os.environ.get('EFI_FILES_STORE_PATH')
    EFI_KOD_SOFTVERA = None
    EFI_SERVICE_URL = None
    EFI_VERIFY_PROTOCOL = None
    EFI_VERIFY_URL = None

    HOSTNAME = None

    AGENT_COOKIE_DOMAIN = None
    AGENT_HTTP_RESPONSE_HEADERS = None

    CUSTOMER_COOKIE_DOMAIN = None
    CUSTOMER_HTTP_RESPONSE_HEADERS = None

    JSON_DUMP_OPTIONS = None

    KALAUZ = b'3xTC-KhRXEuK-5tv-Ogiv0Rpn753rhpb4qoe5MEIuNQ='

    OKRUZENJE = None

    PIDFILE_PATH = '.pidfile'

    PRINT_FONT_FILEPATH_REGULAR = os.environ.get('PRINT_FONT_FILEPATH_REGULAR')
    PRINT_FONT_FILEPATH_LIGHT = os.environ.get('PRINT_FONT_FILEPATH_LIGHT')

    SERVER_BIND_ADDRESS = os.environ.get('SERVER_BIND_ADDRESS')
    SERVER_PORT = int(os.environ.get('SERVER_PORT'))
    SERVER_NUMBER_OF_THREADS = 8
    SERVER_SHUTDOWN_TIMEOUT = 60

    SOAP_API_ELAVIRINT_NAMESPACE = None
    SOAP_API_WSDL = None

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

    TIMEZONE = '+02:00'


def config_as_str():
    lines = [
        'line',
        ['CLIENT_CERTIFICATE_STORE', str(podesavanja.CLIENT_CERTIFICATE_STORE)],
        'line',
        ['COMPANY_FILESTORE_PATH', str(podesavanja.COMPANY_FILESTORE_PATH)],
        'line',
        ['DECIMAL_PRECISION', str(podesavanja.DECIMAL_PRECISION)],
        'line',
        ['EFI_FILES_STORE', str(podesavanja.EFI_FILES_STORE)],
        ['EFI_KOD_SOFTVERA', str(podesavanja.EFI_KOD_SOFTVERA)],
        ['EFI_SERVICE_URL', str(podesavanja.EFI_SERVICE_URL)],
        ['EFI_VERIFY_PROTOCOL', str(podesavanja.EFI_VERIFY_PROTOCOL)],
        ['EFI_VERIFY_URL', str(podesavanja.EFI_VERIFY_URL)],
        'line',
        ['HOSTNAME', podesavanja.HOSTNAME],
        'line',
    ]

    for ii, (key, value) in enumerate(podesavanja.AGENT_HTTP_RESPONSE_HEADERS.items()):
        lines.append(['AGENT_HTTP_RESPONSE_HEADERS %s' % (ii + 1), '%s: %s' % (key, value)])

    lines += ['line']

    for ii, (key, value) in enumerate(podesavanja.CUSTOMER_HTTP_RESPONSE_HEADERS.items()):
        lines.append(['CUSTOMER_HTTP_RESPONSE_HEADERS %s' % (ii + 1), '%s: %s' % (key, value)])

    lines += ['line']

    for ii, (key, value) in enumerate(podesavanja.JSON_DUMP_OPTIONS.items()):
        lines.append(['JSON_DUMP_OPTIONS %s' % (ii + 1), '%s=%s' % (key, value)])

    lines += [
        'line',
        ['KALAUZ', str(podesavanja.KALAUZ)],
        'line',
        ['OKRUZENJE', okruzenje],
        'line',
        ['PIDFILE_PATH', str(podesavanja.PIDFILE_PATH)],
        'line',
        ['PRINT_FONT_FILEPATH_LIGHT', str(podesavanja.PRINT_FONT_FILEPATH_LIGHT)],
        ['PRINT_FONT_FILEPATH_REGULAR', str(podesavanja.PRINT_FONT_FILEPATH_REGULAR)],
        'line',
        ['SERVER_BIND_ADDRESS', str(podesavanja.SERVER_BIND_ADDRESS)],
        ['SERVER_NUMBER_OF_THREADS', str(podesavanja.SERVER_NUMBER_OF_THREADS)],
        ['SERVER_PORT', str(podesavanja.SERVER_PORT)],
        ['SERVER_SHUTDOWN_TIMEOUT', str(podesavanja.SERVER_SHUTDOWN_TIMEOUT)],
        'line',
        ['SOAP_API_ELAVIRINT_NAMESPACE', str(podesavanja.SOAP_API_ELAVIRINT_NAMESPACE)],
        ['SOAP_API_WSDL', str(podesavanja.SOAP_API_WSDL)],
        'line',
        ['SQLALCHEMY_DATABASE_URI', str(podesavanja.SQLALCHEMY_DATABASE_URI)],
        'line',
        ['TIMEZONE', str(podesavanja.TIMEZONE)],
        'line'
    ]

    max_key_len = 0
    max_val_len = 0
    for line in lines:
        if isinstance(line, list):
            max_key_len = max(max_key_len, len(line[0]))
            max_val_len = max(max_val_len, len(line[1]))

    border_text = '|-%s-|-%s-|\n' % ('-' * max_key_len, '-' * max_val_len)
    key_value_format = '| %s | %s |\n'

    config_text = ''
    for line in lines:
        if line == 'line':
            config_text += border_text
        elif isinstance(line, list):
            config_text += key_value_format % (line[0].ljust(max_key_len), line[1].ljust(max_val_len))
        else:
            raise ValueError()

    return config_text


class RazvojnaPodesavanja(OsnovaPodesavanja):
    HOSTNAME = 'http://testpos.e-lavirint.com'

    EFI_KOD_SOFTVERA = 'th528fm074'
    EFI_SERVICE_URL = 'https://efitest.tax.gov.me/fs-v1/'
    EFI_VERIFY_PROTOCOL = 'https'
    EFI_VERIFY_URL = 'efitest.tax.gov.me/ic/#/verify'

    SOAP_API_ELAVIRINT_NAMESPACE = 'http://testpos.elavirint.com/api/xml/schema'
    SOAP_API_WSDL = 'test.wsdl'

    JSON_DUMP_OPTIONS = {
        "indent": 4,
        "sort_keys": True
    }

    AGENT_COOKIE_DOMAIN = '.agent.pos.local'
    AGENT_HTTP_RESPONSE_HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'PUT, GET, POST, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token',
    }

    CUSTOMER_COOKIE_DOMAIN = '192.168.1.200'
    CUSTOMER_HTTP_RESPONSE_HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'PUT, GET, POST, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token',
    }


class ProdukcionaPodesavanja(OsnovaPodesavanja):
    HOSTNAME = 'http://pos.e-lavirint.com'

    EFI_KOD_SOFTVERA = 'gg387fl042'
    EFI_SERVICE_URL = 'https://efi.tax.gov.me/fs-v1'
    EFI_VERIFY_PROTOCOL = 'https'
    EFI_VERIFY_URL = 'mapr.tax.gov.me/ic/#/verify'

    SOAP_API_ELAVIRINT_NAMESPACE = 'http://pos.elavirint.com/api/xml/schema'
    SOAP_API_WSDL = 'api.wsdl'

    JSON_DUMP_OPTIONS = {
        "indent": None,
        "sort_keys": False
    }

    AGENT_COOKIE_DOMAIN = '.e-lavirint.com'
    AGENT_HTTP_RESPONSE_HEADERS = {
        'Access-Control-Allow-Origin': 'http://pos.e-lavirint.com',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'PUT, GET, POST, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token',
    }

    CUSTOMER_COOKIE_DOMAIN = '.e-lavirint.com'
    CUSTOMER_HTTP_RESPONSE_HEADERS = {
        'Access-Control-Allow-Origin': 'http://pos.e-lavirint.com',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'PUT, GET, POST, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token',
    }


okruzenje = os.environ.get('OKRUZENJE')
if okruzenje == 'razvoj':
    podesavanja = RazvojnaPodesavanja
elif okruzenje == 'produkcija':
    podesavanja = ProdukcionaPodesavanja
else:
    print(okruzenje)
    raise Exception(f'Okruženje "{okruzenje}" nije prepoznato')
