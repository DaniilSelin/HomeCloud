import pika
import json
import logging

# Настройка подключения к RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))  # Замените 'localhost' на хост вашего RabbitMQ
channel = connection.channel()

# Объявляем две очереди для логов (информационные и ошибки)
channel.queue_declare(queue='log_info_queue')
channel.queue_declare(queue='log_error_queue')

# Настраиваем логгер
logger = logging.getLogger('log_sender')
logger.setLevel(logging.INFO)


# Функция для отправки логов в очередь RabbitMQ
def send_logInfo(log_record):
    log_record['service'] = "auth_service"

    log_data = json.dumps(log_record)

    channel.basic_publish(exchange='', routing_key='log_info_queue', body=log_data)


def send_logError(log_record):
    log_record['service'] = "auth_service"

    log_data = json.dumps(log_record)

    channel.basic_publish(exchange='', routing_key='log_error_queue', body=log_data)

