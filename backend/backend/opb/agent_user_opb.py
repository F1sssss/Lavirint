import typing as t

from passlib.handlers.pbkdf2 import pbkdf2_sha256

from backend.db import db
from backend.models import AgentUser


def get_by_id(agent_user_id: int) -> [AgentUser, None]:
    return db.session.query(AgentUser).get(agent_user_id)


def get_by_username(username: str) -> t.Optional[AgentUser]:
    return db.session.query(AgentUser).filter(AgentUser.username == username).first()


def check_password(agent_user: AgentUser, plain_password: str) -> bool:
    return pbkdf2_sha256.verify(plain_password, agent_user.password)
