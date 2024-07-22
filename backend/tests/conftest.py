import os
from urllib.parse import urlparse

import pytest
import requests
import sqlalchemy

from backend.db import db


@pytest.fixture(scope="session")
def authenticated_session():
    session = requests.Session()

    session.post('http://localhost:9100/api/login', json={
        'pib': '02700786',
        'email': 'dragana',
        'lozinka': 'dragana5294!'
    })

    yield session

    session.post('http://localhost:9100/api/odjava')


@pytest.fixture(scope="session")
def database(worker_id):
    test_db_name = f"test_megas_{worker_id}"
    test_db_uri = urlparse(str(db.engine.url))._replace(path=test_db_name).geturl()

    test_db = sqlalchemy.create_engine(
        test_db_uri, echo=False, isolation_level="AUTOCOMMIT", client_encoding="utf8"
    )

    try:
        result = test_db.execute(sqlalchemy.sql.text(f"CREATE DATABASE {test_db_name}"))
        result.close()
    except sqlalchemy.exc.ProgrammingError:
        pass
    finally:
        test_db.dispose()


@pytest.fixture
def os_environ():
    """
    clear os.environ, and restore it after the test runs
    """
    # for use whenever you expect code to edit environment variables
    old_env = os.environ.copy()
    os.environ.clear()

    yield

    # clear afterwards in case anything extra was added to the environment during the test
    os.environ.clear()
    for k, v in old_env.items():
        os.environ[k] = v
