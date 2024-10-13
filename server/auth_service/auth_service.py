import os
from views import auth_blueprint, create_first_admin
from flask import Flask
from database.connection import engine
from models import Base
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла, если он существует
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Список обязательных переменных
required_vars = ['JWT_SECRET_KEY', 'ADMIN_SECRET_KEY']

# Проверка, что все обязательные переменные установлены, либо в системе, либо в .env
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Не удалось загрузить следующие обязательные переменные: {', '.join(missing_vars)}")

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ALGORITHM'] = 'HS256'

# Инициализация JWTManager
jwt = JWTManager(app)

Base.metadata.drop_all(engine) # если накосячил с таблицами
Base.metadata.create_all(engine)

with app.app_context():
    try:
        print(
            create_first_admin()
        )
    except Exception as e:
        print(e)

# Импортируем и регистрируем Blueprint -> views.py
app.register_blueprint(auth_blueprint, url_prefix='/')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
