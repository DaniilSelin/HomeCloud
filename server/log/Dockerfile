FROM ubuntu:latest
LABEL authors="Daniil_auth_service"

COPY ./logging_config.py ./logging_config.py

COPY ./LOG_service.py ./LOG_service.py

# Установим Python и pip, очистим кэш, мейби уменьшит образ
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /venv

RUN /venv/bin/pip install pika==1.3.2

# Открываем порт RabbitMQ
EXPOSE 5672

CMD ["/venv/bin/python", "LOG_service.py", "&"]