import threading
import time

import pymysql.err
import pytest
import sqlalchemy.exc
from pymysql.constants import ER
from sqlalchemy import text

from backend.db import db
from backend.opb import faktura_opb


def test_invoice_processing_lock_timing_out():
    stop_event = threading.Event()

    def thread_worker():
        req1 = faktura_opb.InvoiceProcessing()
        with req1.acquire_lock(1) as _:
            while not stop_event.is_set():
                time.sleep(1)

    thread = threading.Thread(target=thread_worker)
    thread.start()

    time.sleep(1)

    connection = db.engine.connect()
    connection.execute(text('SET innodb_lock_wait_timeout=3'))
    low_timeout_session = db.create_session(bind=connection)
    with pytest.raises(sqlalchemy.exc.OperationalError) as excinfo:
        req2 = faktura_opb.InvoiceProcessing()
        with req2.acquire_lock(1, session=low_timeout_session) as _:
            time.sleep(6)

    assert isinstance(excinfo.value.orig, pymysql.err.OperationalError)
    assert excinfo.value.orig.args[0] == ER.LOCK_WAIT_TIMEOUT

    stop_event.set()
    thread.join()


def test_invoice_processing_lock_released_before_timeout():
    def thread_worker():
        req1 = faktura_opb.InvoiceProcessing()
        with req1.acquire_lock(1) as _:
            time.sleep(4)

    thread = threading.Thread(target=thread_worker)
    thread.start()

    time.sleep(1)

    connection = db.engine.connect()
    connection.execute(text('SET innodb_lock_wait_timeout=50'))
    high_timeout_session = db.create_session(bind=connection)
    req2 = faktura_opb.InvoiceProcessing()
    with req2.acquire_lock(1, session=high_timeout_session) as _:
        time.sleep(6)
