# Legacy 2021

## Postavka projekta

Install python dependencies:

    pip3 install -r python-biblioteke.txt


## Lifecylce

### Running the server 

To run server for development/testing run command: 

    make run

To run the server as background process run command:

    make run-background

On server startup the process PID is saved in a file. Location of PID file is specified in `PIDFILE_PATH` environment variable. If PID file already exists the  

To stop the server run command:

    make stop

Shutdown should be initiated with SIGTERM or SIGINT signals. When shutting down, the server closes all connections resulting in '503 Service Unavaliable' responses to clients. However, server will wait for all active requests' workload to finish, but after a timeout it will forcibly close all threads regardless of the remaning workload. Timeout is specified in seconds in `SERVER_SHUTDOWN_TIMEOUT` environment variable 

### Commands

Stopping the server gracefully:
    
    make stop

## Abbreviations

| English | Montenegrin | Description                                                                                                                    |
|---------|-------------|--------------------------------------------------------------------------------------------------------------------------------|
| CA      | --          | Registered certificate authority                                                                                               |                                                                                                     
| CIS     | --          | EFI Central information system; Central invoice register                                                                       |                                                                                                      
| CRL     | --          | List of recalled certificates                                                                                                  |                                                                                                      
| FIC     | JIKR        | Unique invoice code                                                                                                            |                                                                                                       
| GUID    | --          | Global unique identifier                                                                                                       |                                                                                                       
| IIC     | IKOF        | Taxpayer identifying code                                                                                                      |                                                                                                       
| --      | JMB         | National unique identifying number                                                                                             |                                                                                                      
| TIN     | PIB         | Tax identifying number                                                                                                         |                                                                                                      
| OCSP    | --          | Certificate status online protocol                                                                                             |                                                                                                       
| SCP     | SEP         | Self-care EFI portal – web portal that the taxpayer uses for adding specific data, and for other uses in fiscalization process |                                                                                                      
| SOAP    | --          | XML message exchange protocol as specified on https://www.w3.org/TR/soap/                                                      |                                                                                                       
| TCR     | ENU         | Taxpayer's electronic device.                                                                                                  |                                                                                                      
| UC      | --          | Use case diagrams                                                                                                              |                                                                                                     
| UUID    | UJI         | Universal unique identifier                                                                                                    |                                                                                                      
| WSDL    | --          | XML based language that provides web service description, as specified on http://www.w3.org/TR/wsdl                            |                                                                                                       
| UPB     | --          | Unit price before added tax and rebate                                                                                         |                                                                                                       
| UPA     | --          | Unit price after tax and rebate                                                                                                |                                                                                                       


## Locking operations

All endpoints that deal with fiscalisation must be wrapped in the following context to ensure that the invoice numbers are kept in a correct sequence:

```python
import backend.opb.faktura_opb

payment_device_id = '...'

with faktura_opb.invoice_processing_lock(payment_device_id):
    # ...
    pass
```

Locking is based on database row-lock in the table `payment_device_lock`.


## Configuration

| Config                         | Type        |                                                                           |
|--------------------------------|-------------|---------------------------------------------------------------------------|
| CLIENT_CERTIFICATE_STORE       | Environment | Filepath to folder where certificates are stored.                         |
| COMPANY_FILESTORE_PATH         | Environment | Filepath where company level upload folders are stored.                   |
| DECIMAL_PRECISION `Deprecated` | Hardcoded   | Decimal precision for invoice price calculation.                          |
| EFI_FILES_STORE_PATH           | Environment | Filepath where efi requests, efi responses and invoice prints are stored. |
| EFI_KOD_SOFTVERA               | Hardcoded   | Software manufacturer code provided by tax office.                        |
| EFI_SERVICE_URL                | Hardcoded   | Address used to send requests to tax office service.                      |
| EFI_VERIFY_PROTOCOL            | Hardcoded   | Protocol used to send requests to tax office service.                     |
| EFI_VERIFY_URL                 | Hardcoded   | Tax office invoice verification url.                                      |
| HOSTNAME                       | Hardcoded   | Server hostname.                                                          |
| HTTP_RESPONSE_HEADERS          | Hardcoded   | Headers to send in each response.                                         |
| JSON_DUMP_OPTIONS              | Hardcoded   | Options used when dumping data as JSON.                                   |
| KALAUZ                         | Hardcoded   | Key used to encrypt data.                                                 |
| OKRUZENJE                      | Environment | Name of the environment.                                                  |
| PIDFILE_PATH                   | Hardcoded   | Filepath to file containing last process PID.                             |
| PRINT_FONT_FILEPATH_LIGHT      | Environment | Filepath to light font files used for invoice print.                      |
| PRINT_FONT_FILEPATH_REGULAR    | Environment | Filepath to regular font files used for invoice print.                    |
| SERVER_BIND_ADDRESS            | Environment | WSGI server address.                                                      |
| SERVER_NUMBER_OF_THREADS       | Hardcoded   | WSGI server number of threads                                             |
| SERVER_PORT                    | Environment | WSGI server protocol.                                                     |
| SERVER_SHUTDOWN_TIMEOUT        | Hardcoded   | Number of seconds to wait for WSGI server clear requests and shutdown.    |
| SOAP_API_ELAVIRINT_NAMESPACE   | Hardcoded   | Namespace to use in SOAP requests.                                        |
| SOAP_API_WSDL                  | Hardcoded   | Filepath to WSDL schema for SOAP requests.                                |
| SQLALCHEMY_DATABASE_URI        | Environment | Connection string to database.                                            |
| TIMEZONE                       | Hardcoded   | Timezone used for datetime data.                                          |


Example environment file:
```
CLIENT_CERTIFICATE_STORE=
COMPANY_FILESTORE_PATH=
EFI_FILES_STORE_PATH=
OKRUZENJE=
PRINT_FONT_FILEPATH_LIGHT=
PRINT_FONT_FILEPATH_REGULAR=
SERVER_BIND_ADDRESS=
SERVER_PORT=
SQLALCHEMY_DATABASE_URI=
```