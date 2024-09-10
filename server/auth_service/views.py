from flask import Blueprint, request, jsonify
from models import RegistrationToken, User
from server.database_service.python_database_service.connection import get_bd
import datetime
import uuid, os, time, json
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from flask_jwt_extended import get_jwt, create_access_token, jwt_required
from logging_config import logger

AnswerFromAuthService = {
    "status": "success",
    "message": "Operation completed successfully",
    "data": {
        "id": 1,
        "name": "John Doe"
    }
}


# декоратор для логов
def log_requests_and_responses(func):
    """Декоратор для логирования запросов и ответов"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        request_data = {
            'url': request.url,
            'method': request.method,
            'params': request.args.to_dict(),
            'ip': request.remote_addr,
            'user_id': getattr(request, 'user_id', 'N/A'),
            'admin': getattr(request, 'admin', 'N/A'),
        }

        try:
            response = func(*args, **kwargs)
            if isinstance(response, tuple):
                response_body = response[0] if isinstance(response[0], str) else response[0].get_data(as_text=True)
                status_code = response[1]
            else:
                response_body = response.get_json()
                status_code = response.status_code

            # Преобразуем строку JSON в словарь
            if isinstance(response_body, str):
                try:
                    response_body = json.loads(response_body)
                except json.JSONDecodeError:
                    response_body = {}

            duration = (time.time() - start_time) * 1000
            response_data = {
                'status_code': status_code,
                'response_body': response_body,
                'duration': duration
            }

            # Объединяем данные о запросе и ответе
            log_data = {**request_data, **response_data}
            logger.info('Request and Response', extra=log_data)

            # Если это кортеж, возвращаем его как есть, иначе — объект Response
            if isinstance(response, tuple):
                return response_body, status_code
            else:
                return response
        except Exception as e:
            logger.error('Exception occurred', extra={**request_data, 'duration': (time.time() - start_time) * 1000})
            raise

    return wrapper


# декоратор для отлова стандартных ошибок
def handle_exceptions(func):
    """Декоратор для отлова шаблонных ошибок"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = next(get_bd())
        try:
            return func(db=db, *args, **kwargs)
        except SQLAlchemyError as e:
            db.rollback()
            return jsonify({'error': str(e), 'message': 'Database error occurred'}), 500
        except ValueError as e:
            return jsonify({'error': 'Invalid data', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Unexpected error', 'message': str(e)}), 500

    return wrapper


# декоратор чтобы установить, что фукнция доступна только админам
def admin_required(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()

        # Получаем информацию о пользователе из ключа 'sub'
        identity = claims.get('sub', {})

        # Проверяем наличие ключа 'admin' и его значение
        if not identity.get('admin'):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Only admins can perform this action.'
            }), 403
        return func(*args, **kwargs)

    return wrapper


def create_first_admin():
    db = next(get_bd())

    # Данные для создания администратора
    admin_name = "homeuser"
    admin_password = "changeme"

    # Проверяем, существуют ли уже пользователи в базе данных
    user_count = db.query(User).count()

    if user_count == 0:
        # Если пользователей нет, создаем администратора
        new_admin = User(
            user_name=admin_name,
            password=admin_password,
            admin=True,
        )

        # Сохраняем нового пользователя в базу данных
        db.add(new_admin)
        db.commit()

        return "Admin create successfully"
    else:
        return "Admin exist"


class AuthService:
    """
    AuthService предоставляет набор статических методов для
    """
    @staticmethod
    @handle_exceptions
    def generate_token(db, data):
        expiry_days = data.get('expiry', 30)

        token = RegistrationToken.generate_token(expiry_days)

        db.add(token)
        db.commit()

        return jsonify({'message': 'Token created successfully',
                        'data': {'token': token.token, 'expiry_date': token.expiry_date}}), 201

    @staticmethod
    @handle_exceptions
    def get_tokens(db):
        tokens = db.query(RegistrationToken).all()

        # Преобразуем объекты в словари для JSON сериализации
        tokens_list = [{
            'token': t.token,
            'created_at': t.created_at.isoformat(),
            "expiry_date": t.expiry_date.isoformat(),
            "max_users": t.max_users
        } for t in tokens]

        return jsonify({
            'message': 'Tokens retrieved successfully',
            "data": tokens_list
        }), 200

    @staticmethod
    @handle_exceptions
    def update_token_expiry(db, data):
        token = data.get("token", None)
        expiry = data.get('expiry', 30)

        if token is None:
            return jsonify({'error': 'Token is required', 'message': 'Failed to update token expiry'}), 400

        if isinstance(token, str):
            token = uuid.UUID(token)

        reqToken = db.query(
            RegistrationToken).filter(
            RegistrationToken.token == token).first()

        if reqToken is None:
            return jsonify({'error': 'Token not found', 'message': 'Failed to update token expiry'}), 404

        reqToken.expiry_date = datetime.datetime.utcnow() + datetime.timedelta(days=expiry)
        db.commit()

        return jsonify({
            'message': 'Token expiry update successfully',
            "data": {'token': token, 'expiry_date': reqToken.expiry_date}
            }), 201

    @staticmethod
    @handle_exceptions
    def delete_expired_token(db):
        db.query(
            RegistrationToken).filter(
            RegistrationToken.expiry_date < datetime.datetime.utcnow()
        ).delete(synchronize_session=False)  # вроде ускоряет массовые операции
        # а если учесть непоредленное число токенов, то думаю это просто тут необходимо

        db.commit()

        return jsonify({
            'message': 'All expired Token delete',
            "data": {}
        }), 200

    @staticmethod
    @handle_exceptions
    def delete_token(db, data):
        token = data.get("token", None)

        if token is None:
            return jsonify({'error': 'Token is required', 'message': f'Failed to delete token'}), 400

        token_to_delete = db.query(
            RegistrationToken).filter(
            RegistrationToken.token == token
        ).first()  # ускоряет массовые операции

        if token_to_delete is None:
            return jsonify({'error': 'Token not found', 'message': f'Failed to delete token'}), 404

        db.delete(token_to_delete)

        db.commit()

        return jsonify({
            'message': f'Token {token} delete successfully',
            "data": {}
        }), 200

    @staticmethod
    @handle_exceptions
    def set_max_users(db,  data):
        token = data.get("token", None)
        max_users = data.get('max_users', None)

        if token is None or max_users is None:
            return jsonify({'error': 'token and max_users is required',
                           'message': 'Failed to set max users token'}), 400

        reqToken = db.query(
            RegistrationToken).filter(
            RegistrationToken.token == token).first()

        if reqToken is None:
            return jsonify({'error': 'Token not found', 'message': 'Failed to set max users token'}), 404

        reqToken.max_users = int(max_users)
        db.commit()

        return jsonify({
            'message': 'Set token max users successfully',
            "data": {'token': token, 'max_users': reqToken.max_users}
        }), 201

    @staticmethod
    @handle_exceptions
    def register_user(db, data):
        # Получаем значения из данных
        token = data.get("token")
        name = data.get('name')
        password = data.get('password')

        # Проверяем наличие всех необходимых полей
        if not token or not name or not password:
            return jsonify({
                'error': 'Missing fields',
                'message': 'Token, name, and password are required.'
            }), 400

        # Проверяем существование регистрационного токена
        reqToken = db.query(RegistrationToken).filter(
            RegistrationToken.token == token).first()

        if reqToken is None:
            return jsonify({
                'error': 'Invalid token',
                'message': 'Registration token not found.'
            }), 404

        if reqToken.expiry_date < datetime.datetime.now():
            return jsonify({
                'error': 'Token is expired',
                'message': 'Registration token is expired'
            }), 404

        new_user = User(
            reqToken=reqToken.token,
            user_name=name,
            password=password,
        )

        # Сохраняем нового пользователя в базу данных
        db.add(new_user)
        db.commit()

        return jsonify({
            'message': 'User registered successfully',
            "data": {
                'user_name': new_user.user_name,
                'user_id': new_user.user_id,
                'password': new_user.password_hash,
            }
        }), 201

    @staticmethod
    @handle_exceptions
    def login_user(db, data):
        # Проверяем наличие имени и пароля в запросе
        name = data.get('name')
        password = data.get('password')

        if not name or not password:
            return jsonify({
                'error': 'Missing credentials',
                'message': 'Both name and password are required.'
            }), 400

        # Проверяем существование пользователя
        user = db.query(User).filter(User.user_name == name).first()

        if user is None:
            return jsonify({
                'error': 'User not found',
                'message': f'User with name "{name}" not found.'
            }), 404

        # Проверяем правильность пароля
        if not user.check_password(password):
            return jsonify({
                'error': 'Incorrect password',
                'message': 'The password provided is incorrect.'
            }), 401

        # Передаем больше информации в identity
        identity = {
            "user_id": str(user.user_id),
            "admin": user.admin
        }

        access_token = create_access_token(identity=identity)

        # Если все проверки прошли успешно
        return jsonify({
            'message': 'Login successful',
            'data': {
                "access_token": access_token
            }
        }), 200

    @staticmethod
    @handle_exceptions
    def get_users(db):
        users = db.query(User).all()

        # Преобразуем объекты в словари для JSON сериализации
        users_list = [{
            'name': u.user_name,
            'created_at': u.created_at.isoformat(),
            "reqToken": u.reqToken,
            "user_id": u.user_id,
            "admin": u.admin
        } for u in users]

        return jsonify({
            'message': 'Users retrieved successfully',
            "data": users_list
        }), 200

    @staticmethod
    @handle_exceptions
    def delete_user(db, data):
        user_name = data.get("user_name", None)

        if user_name is None:
            return jsonify({
                'error': 'user_name is required',
                'message': 'Failed to delete user'
            }), 400

        user_to_delete = db.query(User).filter(User.user_name == user_name).first()

        if user_to_delete is None:
            return jsonify({
                'error': 'User not found',
                'message': f'Failed to delete user {user_name}'
            }), 404

        db.delete(user_to_delete)
        db.commit()

        return jsonify({
            'message': f'User {user_to_delete.user_name} deleted successfully',
            'data': {}
        }), 200

    @staticmethod
    @handle_exceptions
    def get_user_by_id(db, data):
        user_id = data.get("user_id", None)

        if user_id is None:
            return jsonify({
                'error': 'user_id is required',
                'message': 'Failed to get user'
            }), 400

        try:
            if not isinstance(user_id, uuid.UUID):
                user_id = uuid.UUID(user_id)
        except ValueError:
            return jsonify({
                'error': 'Invalid user_id format',
                'message': f'user_id: {user_id} must be a valid UUID'
            }), 400

        user_found = db.query(User).filter(User.user_id == user_id).first()

        if user_found is None:
            return jsonify({
                'error': 'User not found',
                'message': f'Not found user with id={user_id}'
            }), 404

        # Возвращение данных пользователя в виде словаря
        return jsonify({
            'message': 'User found',
            'data': {
                'user_id': str(user_found.user_id),
                'user_name': user_found.user_name,
                'created_at': user_found.created_at.isoformat(),
                'admin': user_found.admin
            }
        }), 200

    @staticmethod
    @handle_exceptions
    def get_user_by_name(db, data):
        user_name = data.get("user_name", None)

        if user_name is None:
            return jsonify({
                'error': 'user_name is required',
                'message': 'Failed to delete user'
            }), 400

        user_found = db.query(User).filter(User.user_name == user_name).first()

        if user_found is None:
            return jsonify({
                'error': 'User not found',
                'message': f'Not found user with name={user_name}'
            }), 404

        # Возвращение данных пользователя в виде словаря
        return jsonify({
            'message': 'User found',
            'data': {
                'user_id': str(user_found.user_id),
                'user_name': user_found.user_name,
                'created_at': user_found.created_at.isoformat(),
                'admin': user_found.admin
            }
        }), 200

    @staticmethod
    @handle_exceptions
    def change_password(db, user_id, data):
        new_password = data.get("new_password")

        if not user_id:
            return jsonify({
                'error': 'User ID is required',
                'message': 'Failed to update password. Please provide a valid user ID.'
            }), 400

        if not new_password or len(new_password) == 0:
            return jsonify({
                'error': 'Invalid password',
                'message': 'Failed to update password. The new password must be at least 1 characters long.'
            }), 400

        user = db.query(User).filter(User.user_id == user_id).first()

        if user is None:
            return jsonify({
                'error': 'User not found',
                'message': f'Failed to update password. No user found with ID {user_id}.'
            }), 404

        user.password_hash = generate_password_hash(new_password)
        db.commit()

        return jsonify({
            'message': 'Password updated successfully',
            "data": {}
        }), 201

    @staticmethod
    @handle_exceptions
    def update_name_user(db, user_id, data):
        new_name = data.get("new_name")

        if not new_name or len(new_name) == 0:
            return jsonify({
                'error': 'Invalid name',
                'message': 'Failed to update name. The new name must be not empty.'
            }), 400

        user = db.query(User).filter(User.user_id == user_id).first()

        if user is None:
            return jsonify({
                'error': 'User not found',
                'message': f'Failed to update name. No user found with ID {user_id}.'
            }), 404

        user.user_name = new_name
        db.commit()

        return jsonify({
            'message': 'Name updated successfully',
            "data": {}
        }), 201

    @staticmethod
    @handle_exceptions
    def set_admin(db, data, user_id):
        user_id_got = data.get("user_id")
        admin_key = data.get("admin_key")

        if user_id_got:
            user_id = user_id_got

        if admin_key != os.getenv("ADMIN_SECRET_KEY"):
            return jsonify({
                'error': 'Invalid admin key',
                'message': 'The provided admin key is incorrect.'
            }), 403

        user = db.query(User).filter(User.user_id == user_id).first()

        if user is None:
            return jsonify({
                'error': 'User not found',
                'message': f'Failed to set admin. No user found with ID {user_id}.'
                }), 404

        user.admin = True
        db.commit()

        return jsonify({
            'message': 'Set admin successfully',
            "data": {}
            }), 201

    @staticmethod
    @handle_exceptions
    def unset_admin(db, data, user_id):
        user_id_got = data.get("user_id")
        admin_key = data.get("admin_key")

        if user_id_got:
            user_id = user_id_got

        if admin_key != os.getenv("ADMIN_SECRET_KEY"):
            return jsonify({
                'error': 'Invalid admin key',
                'message': 'The provided admin key is incorrect.'
            }), 403

        user = db.query(User).filter(User.user_id == user_id).first()

        if user is None:
            return jsonify({
                'error': 'User not found',
                'message': f'Failed to unset admin. No user found with ID {user_id}.'
            }), 404

        user.admin = False
        db.commit()

        return jsonify({
            'message': 'Unset admin successfully',
            "data": {}
        }), 201


# Создаем Blueprint
auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route("/auth/generate_token", methods=["POST"])
@admin_required
@log_requests_and_responses
def generate_token():
    """
    Создает новый токен.

    Запрос:
    json = {"expiry"(опционально): Количество дней до истечения срока действия токена.}

    Ответ:
    {
     "message": Сообщение о создании токена.
     "status": HTTP статус-код 201.
     "data": {'token': token.token, 'expiry_date': token.expiry_date}
    }
    """
    return AuthService.generate_token(data=request.get_json())


@auth_blueprint.route("/auth/get_tokens", methods=["GET"])
@admin_required
@log_requests_and_responses
def get_tokens():
    """
    Возвращает все токены.

    Запрос:
    Нет.

    Ответ:
    {
     "message": Сообщение об успешном получении токенов,
     "status": HTTP статус-код 200,
     "data": [
         {'token': , 'created_at': , "expiry_date": , "max_users": },
         ...
     ]
    }
    """
    return AuthService.get_tokens()


@auth_blueprint.route("/auth/update_token_expiry", methods=["PATCH"])
@admin_required
@log_requests_and_responses
def update_token_expiry():
    """
    Обновляет время действия токена на переданное количество дней.

    Запрос:
    json = {"token": Токен для обновления, "expiry" (опционально): Количество дней до истечения срока действия токена.}

    Ответ:
    {
     "message": Сообщение об успешном обновлении срока действия токена,
     "status": HTTP статус-код 201,
     "data": {'token': , 'expiry_date': }
    }
    """
    return AuthService.update_token_expiry(data=request.get_json())


@auth_blueprint.route("/auth/delete_expired_token", methods=["DELETE"])
@admin_required
@log_requests_and_responses
def delete_expired_token():
    """
    Удаляет все токены, у которых истек срок годности.

    Запрос:
    Нет.

    Ответ:
    {
     "message": Сообщение об успешном удалении всех истекших токенов,
     "status": HTTP статус-код 200,
     "data": {}
    }
    """
    return AuthService.delete_expired_token()


@auth_blueprint.route("/auth/delete_token", methods=["DELETE"])
@admin_required
@log_requests_and_responses
def delete_token():
    """
    Удаляет указанный токен.

    Запрос:
    json = {"token": Токен для удаления.}

    Ответ:
    {
     "message": Сообщение об успешном удалении токена,
     "status": HTTP статус-код 200,
     "data": {}
    }
    """
    return AuthService.delete_token(data=request.get_json())


@auth_blueprint.route("/auth/set_max_users", methods=["PATCH"])
@admin_required
@log_requests_and_responses
def set_max_users():
    """
    Обновляет максимальное количество квот для регистрации.

    Запрос:
    json = {"token": Токен для обновления, "max_users": Максимальное количество пользователей.}

    Ответ:
    {
     "message": Сообщение об успешном обновлении квоты пользователей,
     "status": HTTP статус-код 201,
     "data": {'token': , 'max_users': }
    }
    """
    return AuthService.set_max_users(data=request.get_json())


@auth_blueprint.route('/auth/register', methods=['POST'])
@log_requests_and_responses
def register():
    """
    Создает нового пользователя.

    Запрос:
    json = {"token": Регистрационный токен, "name": Имя пользователя, "password": Пароль}

    Ответ:
    {
     "message": Сообщение об успешной регистрации пользователя,
     "status": HTTP статус-код 201,
     "data": {'user_name': , 'user_id': , 'admin': }
    }
    """
    return AuthService.register_user(data=request.get_json())


@auth_blueprint.route("/auth/login", methods=["POST"])
@log_requests_and_responses
def login():
    """
    Вход в аккаунт.

    Запрос:
    json = {"name": Имя пользователя, "password": Пароль.}

    Ответ:
    {
     "message": Сообщение об успешном входе,
     "status": HTTP статус-код 200,
     "data": {'access_token': }
    }
    """
    return AuthService.login_user(data=request.get_json())


@auth_blueprint.route("/auth/get_users", methods=["GET"])
@jwt_required()
@log_requests_and_responses
def get_users():
    """
    Возвращает список пользователей.

    Запрос:
    Нет.

    Ответ:
    {
     "message": Сообщение об успешном получении списка пользователей,
     "status": HTTP статус-код 200,
     "data": [
         {'name': , 'created_at': , "reqToken": , "user_id": , "admin": },
         ...
     ]
    }
    """
    return AuthService.get_users()


@auth_blueprint.route("/auth/get_user_by_id", methods=["GET"])
@jwt_required()
@log_requests_and_responses
def get_user_by_id():
    """
    Возвращает информацию о пользователе по его ID.

    Запрос:
    args = {"user_id": ID пользователя.}

    Ответ:
    {
     "message": Сообщение об успешном получении данных пользователя,
     "status": HTTP статус-код 200,
     "data": {'user_id': , 'user_name': , 'admin': }
    }
    """
    return AuthService.get_user_by_id(data=request.args)


@auth_blueprint.route("/auth/get_user_by_name", methods=["GET"])
@jwt_required()
@log_requests_and_responses
def get_user_by_name():
    """
    Возвращает информацию о пользователе по его имени.

    Запрос:
    args = {"user_name": Имя пользователя.}

    Ответ:
    {
     "message": Сообщение об успешном получении данных пользователя,
     "status": HTTP статус-код 200,
     "data": {'user_id': , 'user_name': , 'admin': }
    }
    """
    return AuthService.get_user_by_name(data=request.args)


@auth_blueprint.route("/auth/change_password", methods=["PATCH"])
@jwt_required()
@log_requests_and_responses
def change_password():
    """
    Изменяет пароль пользователя.

    Запрос:
    json = {"new_password": Новый пароль.}

    Ответ:
    {
     "message": Сообщение об успешном изменении пароля,
     "status": HTTP статус-код 201,
     "data": {}
    }
    """
    claims = get_jwt()
    user_id = claims.get('sub', {}).get('user_id')
    return AuthService.change_password(user_id=user_id, data=request.get_json())


@auth_blueprint.route("/auth/update_user", methods=["PATCH"])
@jwt_required()
@log_requests_and_responses
def update_name_user():
    """
    Обновляет имя пользователя.

    Запрос:
    json = {"user_id": ID пользователя, "new_name": Новое имя.}

    Ответ:
    {
     "message": Сообщение об успешном обновлении имени пользователя,
     "status": HTTP статус-код 201,
     "data": {}
    }
    """
    claims = get_jwt()
    user_id = claims.get('sub', {}).get('user_id')
    return AuthService.update_name_user(user_id=user_id, data=request.get_json())


@auth_blueprint.route("/auth/set_admin", methods=["PATCH"])
@jwt_required()
@log_requests_and_responses
def set_admin():
    """
    Назначает пользователя администратором. Если не передавать идентнификатор пользоваетля,
     то статус будет выдам тому, кто отправил запрос

    Запрос:
    json = {"user_id"(небязательно): ID пользователя, "admin_key": Ключ, который выдает владелец облака}

    Ответ:
    {
     "message": Сообщение об успешном назначении администратора,
     "status": HTTP статус-код 201,
     "data": {}
    }
    """
    claims = get_jwt()
    user_id = claims.get('sub', {}).get('user_id')
    return AuthService.set_admin(user_id=user_id, data=request.get_json())


@auth_blueprint.route("/auth/unset_admin", methods=["PATCH"])
@jwt_required()
@log_requests_and_responses
def unset_admin():
    """
    Снимает статус администратора с пользователя.

    Запрос:
    json = {"user_id": ID пользователя, "admin_key": Ключ, который выдает владелец облака}

    Ответ:
    {
     "message": Сообщение об успешном снятии статуса администратора,
     "status": HTTP статус-код 201,
     "data": {}
    }
    """
    claims = get_jwt()
    user_id = claims.get('sub', {}).get('user_id')
    return AuthService.unset_admin(user_id=user_id, data=request.get_json())