from backend.db import db
from backend.models import SoapPermission
from backend.models import SoapUser


def get_soap_user_by_username(username):
    return db.session.query(SoapUser) \
        .filter(SoapUser.username == username) \
        .first()


def get_soap_permission_by_user_id_and_company_id(soap_user_id, company_id):
    return db.session.query(SoapPermission) \
        .filter(SoapPermission.soap_user_id == soap_user_id) \
        .filter(SoapPermission.company_id == company_id) \
        .first()
