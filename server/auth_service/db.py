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
engine.connect()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_bd():
    bd = SessionLocal()
    try:
        yield bd
    finally:
        bd.close()