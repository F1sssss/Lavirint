import http.client
import json
import os
import ssl
from datetime import datetime
from decimal import Decimal
from tempfile import NamedTemporaryFile

from cryptography.hazmat._oid import ObjectIdentifier
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import Name


def _get_identification_number(subject: Name):
    for attr in subject:
        if attr.oid == ObjectIdentifier("2.5.4.97"):
            return attr.value.replace("VATME-", "")


class SepClient:

    def __init__(self, certfile, password):
        with open(certfile, "rb") as file:
            pfx_bytes = file.read()

        private_key, certificate, additional_certificates = \
            pkcs12.load_key_and_certificates(pfx_bytes, password.encode())

        pem = None
        try:
            pem = NamedTemporaryFile(delete=False)
            pem.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(password=password.encode())
                )
            )
            pem.write(
                certificate.public_bytes(serialization.Encoding.PEM)
            )
            pem.close()

            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.load_cert_chain(certfile=pem.name, password=password)
            self.connection = http.client.HTTPSConnection(host="sep.tax.gov.me", port=443, context=context)
        finally:
            if pem is not None and os.path.exists(pem.name):
                os.unlink(pem.name)

        self.identification_number = _get_identification_number(certificate.subject)

    def login(self):
        body = json.dumps({
            "username": None,
            "password": None
        })
        headers = {
            "Content-Type": "application/json"
        }
        self.connection.request(method="POST", url="/kickstart/login", body=body, headers=headers)
        response = self.connection.getresponse()
        data = json.loads(response.read())
        self.token = data["token"]

    def get_invoice_errors(self, page=1, per_page=10, start_datetime: datetime = None, end_datetime: datetime = None):
        body = {
            "entityEnum": "INVOICE_ERROR",
            "page": page,
            "perPage": per_page,
            "sortParams": None,
            "filterColumnDataList": [],
            "filterAllValue": None,
            "exactFilter": None
        }

        if start_datetime is not None or end_datetime is not None:
            s = '' if start_datetime is None else start_datetime.strftime('%d.%m.%Y %H:%M')
            e = '' if end_datetime is None else end_datetime.strftime('%d.%m.%Y %H:%M')
            body["filterColumnDataList"].append({
                "name": "IVS_INPUT_CREATION_DATE",
                "value": f"{s}-{e}",
                "valueList": None,
                "exactFilterValue": False,
                "exactFilter": False
            })
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "lang": "ME"
        }
        self.connection.request(method="POST", url="/eficg/api/tables", body=json.dumps(body), headers=headers)
        response = self.connection.getresponse()
        data = json.loads(response.read())

        output = []
        for row in data[0]["tableRows"]:
            output.append({})
            for cell in row["tableRowCells"]:
                column_name = key = cell["columnName"]
                value = cell["value"]

                if column_name == "ERR_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "IVS_INPUT_CREATION_DATE":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "IVS_ISSUE_DATETIME":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "ERR_IVS_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "ERR_CHK_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "ERR_DAT_CREATED":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "CHK_CD":
                    output[-1][key] = value
                elif column_name == "CHK_CD_MSG_ERR":
                    output[-1][key] = value
                elif column_name == "CHK_CD_MSG_REC":
                    output[-1][key] = value
                elif column_name == "ITS_CODE":
                    output[-1][key] = value
                elif column_name == "ITS_DESCRIPTION":
                    output[-1][key] = value
                elif column_name == "IVS_TOTAL_PRICE":
                    output[-1][key] = None if value is None else Decimal(value.replace(",", "."))
                elif column_name == "IVS_BUSINESS_UNIT_CODE":
                    output[-1][key] = value
                elif column_name == "IVS_TCR_CODE":
                    output[-1][key] = value
                elif column_name == "IVS_OPERATOR_CODE":
                    output[-1][key] = value
                elif column_name == "IVS_SOFT_CODE":
                    output[-1][key] = value
                elif column_name == "IVS_FIC":
                    output[-1][key] = value
                elif column_name == "IVS_ISSUER_TIN":
                    output[-1][key] = value
                elif column_name == "IVS_SELLER_NAME":
                    output[-1][key] = value
                elif column_name == "IVS_BUYER_NAME":
                    output[-1][key] = value
                elif column_name == "IVS_BUYER_TIN":
                    output[-1][key] = value
                elif column_name == "IVS_IIC":
                    output[-1][key] = value
                elif column_name == "IS_ISSUED_BY_SCP":
                    output[-1][key] = value
                else:
                    raise KeyError(f"Unknown \"columnName\" {column_name}")
        return output

    def get_taxpayers(self, page=1, per_page=10):
        body = {
            "entityEnum": "TAXPAYERS",
            "page": page,
            "perPage": per_page,
            "sortParams": None,
            "filterColumnDataList": [],
            "filterAllValue": None,
            "exactFilter": None
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "lang": "ME"
        }
        self.connection.request(method="POST", url="/eficg/api/tables", body=json.dumps(body), headers=headers)
        response = self.connection.getresponse()
        data = json.loads(response.read())

        output = []
        for row in data[0]["tableRows"]:
            output.append({})
            for cell in row["tableRowCells"]:
                column_name = key = cell["columnName"]
                value = cell["value"]
                if column_name == "PTY_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_TIN":
                    output[-1][key] = value
                elif column_name == "PSE_PTE_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PSE_CODE":
                    output[-1][key] = value
                elif column_name == "PSE_HAS_PHYSICAL_ATTR":
                    output[-1][key] = value
                elif column_name == "PSE_HAS_ACTIVITIES":
                    output[-1][key] = value
                elif column_name == "PTY_PSE_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_SHORT_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_START_DATE":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "PTY_END_DATE":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "PTY_FIRST_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_MIDDLE_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_LAST_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_MAIDEN_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_GENDER_GDR_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_DATE_OF_BIRTH":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "PTY_EDUCATION_ELL_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_ORU_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "ORU_SUPER_ORU_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_EMP_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_OWNER_PTY_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_USR_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_ROLE_CPRE_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_FATHERS_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_EXTERNAL_ID":
                    output[-1][key] = value
                elif column_name == "PTY_OPERATOR_CODE":
                    output[-1][key] = value
                elif column_name == "PTY_VAT_ID_NUMBER":
                    output[-1][key] = value
                elif column_name == "PTY_PSZ_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "ARS_CNT_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "ARS_MNY_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "ARS_STT_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "ARS_SETTLEMENT_NAME":
                    output[-1][key] = value
                elif column_name == "ARS_STREET_NAME":
                    output[-1][key] = value
                elif column_name == "PSS_CPSS_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "CPSS_CODE":
                    output[-1][key] = value
                elif column_name == "PTY_HAS_VAT":
                    output[-1][key] = value
                elif column_name == "PTY_DSC_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "LAST_UPDATE_DATE":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "PAY_ACT_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "ACT_CODE":
                    output[-1][key] = value
                elif column_name == "CNT_IS_MAIN_COUNTRY":
                    output[-1][key] = value
                else:
                    raise KeyError(f"Unknown \"columnName\" {column_name}")
        return output

    def get_operators(self, page=1, per_page=10):
        body = {
            "entityEnum": "TAXPAYER_OPERATORS",
            "page": page,
            "perPage": per_page,
            "sortParams": None,
            "filterColumnDataList": [],
            "filterAllValue": None,
            "exactFilter": None
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "lang": "ME"
        }
        self.connection.request(method="POST", url="/eficg/api/tables", body=json.dumps(body), headers=headers)
        response = self.connection.getresponse()
        data = json.loads(response.read())

        output = []
        for row in data[0]["tableRows"]:
            output.append({})
            for cell in row["tableRowCells"]:
                column_name = key = cell["columnName"]
                value = cell["value"]
                if column_name == "OPR_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "OPR_EMPLOYER_PTY_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_TIN":
                    output[-1][key] = value
                elif column_name == "PTY_ARS_MNY_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_ARS_STR_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "MNY_NAME_LOCAL":
                    output[-1][key] = value
                elif column_name == "STR_NAME_LOCAL":
                    output[-1][key] = value
                elif column_name == "OPR_OPERATOR_CODE":
                    output[-1][key] = value
                elif column_name == "OPR_FIRST_NAME":
                    output[-1][key] = value
                elif column_name == "OPR_MIDDLE_NAME":
                    output[-1][key] = value
                elif column_name == "OPR_LAST_NAME":
                    output[-1][key] = value
                elif column_name == "OPR_ID_NUMBER":
                    output[-1][key] = value
                elif column_name == "VALID_FROM":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "VALID_TO":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                else:
                    raise KeyError(f"Unknown \"columnName\" {column_name}")
        return output

    def get_cash_registers(self, page=1, per_page=10, swe_code=None):
        body = {
            "entityEnum": "CASH_REGISTERS",
            "page": page,
            "perPage": per_page,
            "sortParams": None,
            "filterColumnDataList": [],
            "filterAllValue": None,
            "exactFilter": None
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "lang": "ME"
        }

        if swe_code is not None:
            body["filterColumnDataList"].append({
                "name": "SWE_CODE",
                "value": swe_code,
                "valueList": None,
                "exactFilterValue": False,
                "exactFilter": False
            })

        self.connection.request(method="POST", url="/eficg/api/tables", body=json.dumps(body), headers=headers)
        response = self.connection.getresponse()
        data = json.loads(response.read())

        output = []
        for row in data[0]["tableRows"]:
            output.append({})
            for cell in row["tableRowCells"]:
                column_name = key = cell["columnName"]
                value = cell["value"]
                if column_name == "BDE_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "BDE_CODE":
                    output[-1][key] = value
                elif column_name == "PTY_TIN":
                    output[-1][key] = value
                elif column_name == "PTY_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_ARS_MNY_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "PTY_ARS_STR_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "MNY_NAME_LOCAL":
                    output[-1][key] = value
                elif column_name == "STR_NAME_LOCAL":
                    output[-1][key] = value
                elif column_name == "PTY_PSE_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "BUT_NAME":
                    output[-1][key] = value
                elif column_name == "BUT_ARS_MNY_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "BUT_ARS_STR_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "MNY_NAME":
                    output[-1][key] = value
                elif column_name == "STR_NAME":
                    output[-1][key] = value
                elif column_name == "BDE_BNS_UNT_BUT_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "BDE_ORDER_NUMBER":
                    output[-1][key] = value
                elif column_name == "BDE_SOFTWARE_SWE_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "BDE_SOFT_MAINT_SCE_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "BDE_TELECOM_SCE_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "BDE_LOCATION":
                    output[-1][key] = value
                elif column_name == "BDE_TYPE_BTE_ID":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "BDE_TYPE_BTE_ID_INSERT":
                    output[-1][key] = None if value is None else int(value)
                elif column_name == "VALID_FROM":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "VALID_TO":
                    output[-1][key] = None if value is None else datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
                elif column_name == "PTY_PRODUCER_NAME":
                    output[-1][key] = value
                elif column_name == "SPR_NAME":
                    output[-1][key] = value
                elif column_name == "SWE_CODE":
                    output[-1][key] = value
                elif column_name == "SWE_VERSION":
                    output[-1][key] = value
                elif column_name == "PTY_MAINTAINER_NAME":
                    output[-1][key] = value
                elif column_name == "PTY_MAINTAINER_TIN":
                    output[-1][key] = value
                elif column_name == "CPSS_CODE":
                    output[-1][key] = value
                else:
                    raise KeyError(f"Unknown \"columnName\" {column_name}")
        return output


    def get_producers(self, page=1, per_page=10, swe_code=None):
        body = {
            "entityEnum": "SPECIAL_CATALOGUE_PRODUCERS",
            "page": page,
            "perPage": per_page,
            "sortParams": None,
            "filterColumnDataList": [],
            "filterAllValue": None,
            "exactFilter": None
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "lang": "ME"
        }

        if swe_code is not None:
            body["filterColumnDataList"].append({
                "name": "SWE_CODE",
                "value": swe_code,
                "valueList": None,
                "exactFilterValue": False,
                "exactFilter": False
            })

        self.connection.request(method="POST", url="/eficg/api/tables", body=json.dumps(body), headers=headers)
        response = self.connection.getresponse()
        data = json.loads(response.read())

        output = []
        for row in data[0]["tableRows"]:
            output.append({})
            for cell in row["tableRowCells"]:
                column_name = key = cell["columnName"]
                value = cell["value"]
                print(column_name, cell["dataType"])
        return output
