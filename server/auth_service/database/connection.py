from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import Config
from sqlalchemy.exc import OperationalError
import time

"""
Файл для подключения к бд
По факту это не сервис, а просто место откуда все контенеры могу брать соединение с бд
"""


# Подключаем базу данных
def connect_to_database():
    try:
        # Создаем движок подключения
        engine = create_engine(
            Config.SQLALCHEMY_DATABASE_URI,
            echo=True,
            pool_size=6
        )
        # Пытаемся подключиться к базе данных
        connection = engine.connect()
        return engine, connection
    except OperationalError as e:
        time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
        return connect_to_database()


# Вызываем функцию подключения
engine, connection = connect_to_database()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_bd():
    bd = SessionLocal()
    try:
        yield bd
    finally:
        bd.close()