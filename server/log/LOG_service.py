import pika
import pika.exceptions
import json
import time
from logging_config import logger


# Функция для установки соединения с RabbitMQ
def connect_to_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
        channel = connection.channel()
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f'Failed to connect to RabbitMQ: {e}')
        time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
        return connect_to_rabbitmq()


connection, channel = connect_to_rabbitmq()

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
    # Подтверждение обработки сообщения
    ch.basic_ack(delivery_tag=method.delivery_tag)


def CallbackLogError(ch, method, properties, body):
    try:
        log_record = json.loads(body)
        logger.error('Request and Response', extra=log_record)
    except json.JSONDecodeError as e:
        logger.error(f'Failed to decode JSON: {e}')
    except Exception as e:
        logger.error(f'Error while processing log record: {e}')
    # Подтверждение обработки сообщения
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Подписка на очередь
channel.basic_consume(queue='log_info_queue', on_message_callback=CallbackLogInfo)
channel.basic_consume(queue='log_error_queue', on_message_callback=CallbackLogError)

channel.start_consuming()