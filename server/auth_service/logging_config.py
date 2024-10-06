import json
import pika
import pika.exceptions
import time
import logging


logger = logging.getLogger('simple_logger')
logger.setLevel(logging.ERROR)


# Функция для установки соединения с RabbitMQ
def establish_connection():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
        channel = connection.channel()
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f'Failed to connect to RabbitMQ: {e}')
        time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
        return establish_connection()


connection, channel = establish_connection()


# Функция для восстановления соединения
def recover_connection():
    global connection, channel
    try:
        logger.info("Attempting to recover connection...")
        connection, channel = establish_connection()
    except Exception as e:
        logger.error(f'Failed to recover connection: {e}')


# Функция для отправки логов в очередь RabbitMQ
def send_logInfo(log_record):
    try:
        log_record['service'] = "auth_service"
        log_data = json.dumps(log_record)

        if channel.is_open:
            channel.basic_publish(exchange='', routing_key='log_info_queue', body=log_data)
        else:
            recover_connection()
    except Exception as e:
        log_record['response_body']["error"] = str(e)
        logger.error(f'Error while sending log_info: {e}')
        send_logError(log_record)


# Функция для отправки логов ошибок в очередь RabbitMQ
def send_logError(log_record):
    try:
        log_record['service'] = "auth_service"
        log_data = json.dumps(log_record)

        if channel.is_open:
            channel.basic_publish(exchange='', routing_key='log_error_queue', body=log_data)
        else:
            recover_connection()
    except Exception as e:
        logger.critical(f'Failed to send log_error: {e}')