import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        'postgresql+psycopg2://homecloudauthsevice:123@localhost:5432/homecloud'
                                        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


"""
ПРИМЕЧАНИЯ ЧТОБЫ НЕ ЗАПУТАЦА ТУТА
dialect+driver://username:password@host:port/database

    dialect — это имя базы данных (mysql, postgresql, mssql, oracle и так далее).
    driver — используемый DBAPI. Этот параметр является необязательным. Если его не указать будет использоваться драйвер по умолчанию (если он установлен).
    username и password — данные для получения доступа к базе данных.
    host — расположение сервера базы данных.
    port — порт для подключения.
    database — название базы данных.
"""