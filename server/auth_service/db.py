import os.path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

"""
Файл для подключения к бд
"""

# Подключаем базу данных
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    echo=True, pool_size=6)

connection = engine.connect()

with open(
        os.path.join(os.path.dirname(__file__), "trigger_limiting_usersRtoken.sql")
) as file:
    trigger_sql = file.read()
    connection.execute(trigger_sql)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_bd():
    bd = SessionLocal()
    try:
        yield bd
    finally:
        bd.close()