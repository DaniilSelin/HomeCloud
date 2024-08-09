FROM ubuntu:18.04

WORKDIR /HomeCloud/server/auth_service

COPY . .

RUN pip install -r requrements.txt

EXPOSE 5000

CMD ["python3", "./auth_srvice.py"]
