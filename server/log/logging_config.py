import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
import os


class RequestFilter(logging.Filter):
    def filter(self, record):
        record.service = getattr(record, 'service', 'N/A')
        record.url = getattr(record, 'url', 'N/A')
        record.method = getattr(record, 'method', 'N/A')
        record.params = getattr(record, 'params', 'N/A')
        record.ip = getattr(record, 'ip', 'N/A')
        record.admin = getattr(record, 'admin', 'N/A')
        record.status_code = getattr(record, 'status_code', 'N/A')
        record.duration = getattr(record, 'duration', 'N/A')

        # Фильтрация данных ответа
        response_body = getattr(record, 'response_body', {})
        if "error" in response_body:
            record.response_body = {"error": response_body.get('error', 'N/A'), 'message': response_body.get('message', 'N/A')}
        else:
            record.response_body = {'message': response_body.get('message', 'N/A')}

        return True


# Определите абсолютные пути
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
request_detailed_log = os.path.join(log_dir, 'request/request.log')
error_log = os.path.join(log_dir, 'error/error.log')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': ('%(asctime)s - %(service)s - %(levelname)s - %(message)s - '
                       'ip=%(ip)s - url=%(url)s - '
                       'method=%(method)s - params=%(params)s - '
                       'duration=%(duration)s ms - '
                       'status_code=%(status_code)s - response_body=\n%(response_body)s\n - ')
        },
    },
    'handlers': {
        'file_detailed': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': request_detailed_log,
            'formatter': 'detailed',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,  # Хранить до 5 файлов логов
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': error_log,
            'formatter': 'detailed',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,  # Хранить до 5 файлов логов
        },
    },
    'loggers': {
        'auth_service': {
            'handlers': ['file_detailed', 'file_error'],
            'level': 'INFO',
            'propagate': True,
            'filters': ['request_filter'],
        },
    },
    'filters': {
        'request_filter': {
            '()': RequestFilter,
        }
    }
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger()
