from flask import Blueprint, request, jsonify
from models import RegistrationToken, User
from server.database_service.connection import get_bd
import datetime
import uuid
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps

AnswerFromAuthService = {
    "status": "success",
    "message": "Operation completed successfully",
    "data": {
        "id": 1,
        "name": "John Doe"
    }
}


def handle_exceptions(func):
    """Декоратор для отлова шаблонных ошибок"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = next(get_bd())
        try:
            return func(db, *args, **kwargs)
        except SQLAlchemyError as e:
            db.rollback()
            return jsonify({'error': str(e), 'message': 'Database error occurred'}), 500
        except ValueError as e:
            return jsonify({'error': 'Invalid data', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Unexpected error', 'message': str(e)}), 500

    return wrapper


class AuthService:
    @staticmethod
    @handle_exceptions
    def generate_token(db, data):
        expiry_days = data.get('expiry', 30)

        token = RegistrationToken(
            token=str(uuid.uuid4()),
            expiry_date=datetime.datetime.utcnow() + datetime.timedelta(days=expiry_days)
        )

        db.add(token)
        db.commit()

        return jsonify({'message': 'Token created successfully'}), 201

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
    def set_max_users(db, data):
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
        admin = data.get("admin", False)

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
            admin=admin
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
                'admin': new_user.admin
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

        # Если все проверки прошли успешно
        return jsonify({
            'message': 'Login successful',
            'data': {
                'user_id': user.user_id,
                'user_name': user.user_name
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
            user_id = uuid.UUID(user_id)
        except ValueError:
            return jsonify({
                'error': 'Invalid user_id format',
                'message': 'user_id must be a valid UUID'
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
    def change_password(db, data):
        user_id = data.get("user_id")
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
    def update_name_user(db, data):
        user_id = data.get("user_id")
        new_name = data.get("new_name")

        if not user_id:
            return jsonify({
                'error': 'User ID is required',
                'message': 'Failed to update name. Please provide a valid user ID.'
            }), 400

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
    def set_admin(db, data):
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({
                'error': 'User ID is required',
                'message': 'Failed to set admin. Please provide a valid user ID.'
                }), 400

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
    def unset_admin(db, data):
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({
                'error': 'User ID is required',
                'message': 'Failed to set admin. Please provide a valid user ID.'
            }), 400

        user = db.query(User).filter(User.user_id == user_id).first()

        if user is None:
            return jsonify({
                'error': 'User not found',
                'message': f'Failed to set admin. No user found with ID {user_id}.'
            }), 404

        user.admin = False
        db.commit()

        return jsonify({
            'message': 'Set admin successfully',
            "data": {}
        }), 201


# Создаем Blueprint
auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route("/auth/generate_token", methods=["POST"])
def generate_token():
    """Создает новый токен"""
    return AuthService.generate_token(data=request.get_json())


@auth_blueprint.route("/auth/get_tokens", methods=["GET"])
def get_tokens():
    """ Возвращает все токены"""
    return AuthService.get_tokens()


@auth_blueprint.route("/auth/update_token", methods=["PATCH"])
def update_token_expiry():
    """ Обновляет время действия токена на переданное количество дней"""
    return AuthService.update_token_expiry(data=request.get_json())


@auth_blueprint.route("/auth/delete_expired_token", methods=["DELETE"])
def delete_expired_token():
    """Удаляет все токены, у которых истек срок годности"""
    return AuthService.delete_expired_token()


@auth_blueprint.route("/auth/delete_token", methods=["DELETE"])
def delete_token():
    """Удаляет указанный токен"""
    return AuthService.delete_token(data=request.get_json())


@auth_blueprint.route("/auth/set_max_users", methods=["PATCH"])
def set_max_users():
    """Обновляет максимальное колчество квот для регистрации"""
    return AuthService.set_max_users(data=request.get_json())


@auth_blueprint.route('/auth/register', methods=['POST'])
def register():
    """Создает нового пользователя"""
    return AuthService.register_user(data=request.get_json())


@auth_blueprint.route("/auth/login", methods=["POST"])
def login():
    """НЕДОПИСАННАЯ ЛОГИКА ВЗОДА В АКАУНТ"""
    return AuthService.login_user(data=request.get_json())


@auth_blueprint.route("/auth/get_users", methods=["GET"])
def get_users():
    """Возвращает список пользоваетелей"""
    return AuthService.get_users()


### ИСПРАВИТЬ!!!! РЕСТ АПИ ПРИДЕРЖИВАЕМСЯ ЧМОНЯ
@auth_blueprint.route("/auth/get_user", methods=["GET"])
def get_user():
    """Возвращает информацию о пользователе по его ID"""
    return AuthService.get_user_by_id(data=request.get_json())


### ИСПРАВИТЬ!!!! РЕСТ АПИ ПРИДЕРЖИВАЕМСЯ ЧМОНЯ
@auth_blueprint.route("/auth/get_user_by_name", methods=["GET"])
def get_user_by_name():
    """Возвращает информацию о пользователе"""
    return AuthService.get_user_by_name(data=request.get_json())


@auth_blueprint.route("/auth/change_password", methods=["PATCH"])
def change_password():
    """Изменяет пароль пользователя"""
    return AuthService.change_password(data=request.get_json())


@auth_blueprint.route("/auth/update_user", methods=["PATCH"])
def update_name_user():
    """Обновляет данные пользователя"""
    return AuthService.update_name_user(data=request.get_json())


@auth_blueprint.route("/auth/set_admin", methods=["PATCH"])
def set_admin():
    """Устанавливает польхователю по id в позицию admin"""
    return AuthService.set_admin(data=request.get_json())


@auth_blueprint.route("/auth/unset_admin", methods=["PATCH"])
def unset_admin():
    """Устанавливает польхователю по id в позицию admin"""
    return AuthService.unset_admin(data=request.get_json())