from threading import get_ident as _ident_func

from sqlalchemy import create_engine
from sqlalchemy import orm
from sqlalchemy import text

from backend.podesavanja import podesavanja


class SQLAlchemy:

    def __init__(self, app=None, connect_args=None):
        connect_args = connect_args or {}

        self.app = app
        self.engine = create_engine(podesavanja.SQLALCHEMY_DATABASE_URI,
                                    pool_size=100, pool_recycle=280, connect_args=connect_args)
        self.session = self.create_scoped_session()
        self.Query = orm.Query

    def create_scoped_session(self):
        session = orm.sessionmaker(bind=self.engine)
        return orm.scoped_session(session, scopefunc=_ident_func)

    def create_session(self, bind=None):
        if bind is None:
            create_session = orm.sessionmaker(bind=self.engine)
        else:
            create_session = orm.sessionmaker(bind=bind)

        return create_session()

    def execute(self, sql, **kwargs):
        statement = text(sql)
        with self.engine.connect() as connection:
            return connection.execute(statement, **kwargs)


db = SQLAlchemy()
