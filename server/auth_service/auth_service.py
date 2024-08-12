from flask import Flask
from server.database_service.connection import engine
from models import Base

app = Flask(__name__)
#Base.metadata.drop_all(engine) # если накосячил с таблицами
Base.metadata.create_all(engine)

# Импортируем и регистрируем Blueprint -> views.py
from views import auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)