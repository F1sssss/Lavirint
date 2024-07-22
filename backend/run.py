import os
import signal
import sys
import threading
import time
from datetime import datetime

from cheroot.wsgi import Server as WSGIServer

from backend import create_app
from backend import pidfile
from backend.logging import cli_logger
from backend.podesavanja import config_as_str
from backend.podesavanja import podesavanja

cli_logger.info('Service startup: \n' + config_as_str())

pidfile.ensure_path()
pidfile.append_current()

server = WSGIServer(
    bind_addr=(podesavanja.SERVER_BIND_ADDRESS, podesavanja.SERVER_PORT),
    wsgi_app=create_app(),
    server_name='Megas',
    numthreads=podesavanja.SERVER_NUMBER_OF_THREADS,
    shutdown_timeout=podesavanja.SERVER_SHUTDOWN_TIMEOUT
)


def gracefull_shutdown(signal_number, frame):
    now = datetime.now()
    cli_logger.info('Received %s. Stopping server.' % signal.Signals(signal_number).name)
    server.stop()

    if (datetime.now() - now).total_seconds() > server.shutdown_timeout:
        cli_logger.warning('Timed out after %s. Some requests did not finish workload.' % server.shutdown_timeout)
    else:
        cli_logger.info('Server stopped gracefully')

    pidfile.remove_current()

    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, gracefull_shutdown)
    signal.signal(signal.SIGINT, gracefull_shutdown)

    try:
        threading.Thread(target=server.start).start()
        if os.name != 'nt':
            signal.pause()
        else:
            while True:
                time.sleep(5)

    except SystemExit:
        cli_logger.info('Exiting')
    except Exception:
        cli_logger.exception("Server stopped due to an error")
