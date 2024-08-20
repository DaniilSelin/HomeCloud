import os
from views import auth_blueprint, create_first_admin
from flask import Flask
from server.database_service.connection import engine
from models import Base

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# Base.metadata.drop_all(engine) # если накосячил с таблицами
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
