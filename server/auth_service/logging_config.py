import json
import pika
import pika.exceptions
import time
import logging


logger = logging.getLogger('simple_logger')
logger.setLevel(logging.ERROR)

# Список возможных способов подключения
connection_params = [
    {"host": "rabbitmq", "description": "hostname 'rabbitmq'"},
    {"host": "localhost", "description": "localhost"},
    {"host": "172.17.0.2", "description": "IP address '172.17.0.2'"},  # IP-адрес можно настроить динамически
]


def establish_connection(attempt=0):
    if attempt >= len(connection_params):
        logger.error("All connection attempts failed. No more methods to try. Retry")
        return establish_connection()

    # Выбираем текущий способ подключения
    current_method = connection_params[attempt]
    host = current_method['host']
    description = current_method['description']

    try:
        logger.info(f"Trying to connect to RabbitMQ using {description}...")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        logger.info(f"Successfully connected to RabbitMQ using {description}")
        return connection, channel
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ using {description}: {e}")
        time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
        return establish_connection(attempt + 1)


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