import logging
import threading
import time
from functools import wraps
from logging.handlers import WatchedFileHandler

import bottle
from pythonjsonlogger.jsonlogger import JsonFormatter as BaseJSONFormatter

LOG_FORMAT = '%(asctime)s %(app_name)s %(name)s %(levelname)s %(endpoint)s %(request_id)s "%(message)s" [in %(pathname)s:%(lineno)d]'  # noqa: E501
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class FiscalisationLogger(logging.Logger):

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        rv = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func, sinfo)
        if extra is not None:
            rv.__dict__['extra'] = extra
        return rv


class JSONFormatter(BaseJSONFormatter):

    def __init__(self, app_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_name = app_name

    def process_log_record(self, record):
        rename_map = {
            "asctime": "time",
            "app_name": self.app_name
        }

        for key, newkey in rename_map.items():
            record[newkey] = record.pop(key)
        record['logType'] = 'application'

        try:
            record['message'] = record['message'].format(**record)
        except (KeyError, IndexError) as exception:
            logger.exception("failed to format log message: {} not found".format(exception))
        return record


class SessionIdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(bottle.request, 'session'):
            record.session_id = 'no_session'
        elif bottle.request.session.id is None:
            record.session_id = 'unauthorized'
        else:
            record.session_id = bottle.request.session.id

        return record


class EndpointFilter(logging.Filter):
    def filter(self, record):
        try:
            record.endpoint = bottle.request.route
        except Exception:
            record.endpoint = None

        return record


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = threading.get_ident()
        return record


class ElapsedTimeFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(bottle.request, 'elapsed_time'):
            record.elapsed_time = '---'
        else:
            record.elapsed_time = bottle.request.elapsed_time
        return record


logger = logging.Logger(__name__)
logger.setLevel(level=logging.DEBUG)

file_handler = WatchedFileHandler('customer.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(JSONFormatter("backend.customer", LOG_FORMAT, TIME_FORMAT))
file_handler.addFilter(SessionIdFilter())
file_handler.addFilter(EndpointFilter())
file_handler.addFilter(RequestIdFilter())
file_handler.addFilter(ElapsedTimeFilter())

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.addFilter(ElapsedTimeFilter())
stream_handler.setFormatter(logging.Formatter(
    'time:          %(asctime)s\n'
    'elapsed_time:  %(elapsed_time)s\n'
    'session_id:    %(session_id)s\n'
    'request_id:    %(request_id)s\n'
    'endpoint:      %(endpoint)s\n'
    'level:         %(levelname)s\n'
    'message:       %(msg)s\n\n'
))

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(msg)s')

file_handler = logging.FileHandler('operation.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

cli_logger = logging.Logger(__name__)
cli_logger.setLevel(level=logging.DEBUG)
cli_logger.addHandler(file_handler)
cli_logger.addHandler(stream_handler)


def bottle_logging(callback):
    @wraps(callback)
    def wrapper(*args, **kwargs):
        start = time.time()

        try:
            # TODO XML request bodies are currently not being logged
            return callback(*args, **kwargs)
        except Exception as exception:
            logger.exception('Code %s' % bottle.response.status)

        request_body = None
        if bottle.request.json is not None:
            request_body = bottle.request.json

        try:
            body = callback(*args, **kwargs)
            bottle.request.elapsed_time = str(time.time() - start)

            logger.debug('Code %s' % bottle.response.status, extra={
                'request_body': request_body,
                'response_body': body
            })
            return body
        except Exception as exc:
            bottle.request.elapsed_time = str(time.time() - start)
            bottle.response.status = 500
            logger.exception('Code %s' % bottle.response.status, extra={
                'request_body': request_body,
                'response_body': exc
            })
            raise exc

    return wrapper
