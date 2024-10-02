import pika
import json
from logging_config import logger

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitqm"))
channel = connection.channel()

channel.queue_declare(queue="log_info_queue")
channel.queue_declare(queue="log_error_queue")


def CallbackLogInfo(ch, method, properties, body):
    try:
        log_record = json.loads(body)
        logger.info('Request and Response', extra=log_record)
    except json.JSONDecodeError as e:
        logger.error(f'Failed to decode JSON: {e}')
    except Exception as e:
        logger.error(f'Error while processing log record: {e}')


def CallbackLogError(ch, method, properties, body):
    try:
        log_record = json.loads(body)
        logger.error('Request and Response', extra=log_record)
    except json.JSONDecodeError as e:
        logger.error(f'Failed to decode JSON: {e}')
    except Exception as e:
        logger.error(f'Error while processing log record: {e}')


# Подписка на очередь
channel.basic_consume(queue='log_info_queue', on_message_callback=CallbackLogInfo, auto_ack=True)
channel.basic_consume(queue='log_error_queue', on_message_callback=CallbackLogError, auto_ack=True)

channel.start_consuming()