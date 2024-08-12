from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.database_service.config import Config

"""
Файл для подключения к бд
По факту это не сервис, а просто место откуда все контенеры могу брать соединение с бд
"""

# Подключаем базу данных
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    echo=True, pool_size=6)

connection = engine.connect()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_bd():
    bd = SessionLocal()
    try:
        yield bd
    finally:
        bd.close()