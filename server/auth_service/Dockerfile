FROM ubuntu:latest
LABEL authors="Daniil_auth_service"

WORKDIR /server

COPY ./server/__init__.py .

COPY ./server/auth_service ./auth_service

WORKDIR /server/auth_service

# Установите Python и pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libpq-dev \
    build-essential

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

ENV PYTHONPATH="/server:/server/auth_service"

RUN pip3 install -r requirements.txt

EXPOSE 5000

RUN ln -s /server /server/auth_service/server

CMD ["python3", "auth_service.py"]