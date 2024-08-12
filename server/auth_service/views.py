from flask import Blueprint, request, jsonify
from models import RegistrationToken, User
from server.database_service.connection import get_bd
import datetime
from sqlalchemy.exc import SQLAlchemyError

AnswerFromAuthService = {
    "status": "success",
    "message": "Operation completed successfully",
    "data": {
        "id": 1,
        "name": "John Doe"
    }
}


class AuthService:
    @staticmethod
    def generate_token(data):
        import uuid

        db = next(get_bd())

        try:
            expiry_days = data.get('expiry', 30)

            token = RegistrationToken(
                token=str(uuid.uuid4()),
                expiry_date=datetime.datetime.utcnow() + datetime.timedelta(days=expiry_days)
            )

            db.add(token)
            db.commit()

            return jsonify({'message': 'Token created successfully'}), 201

        except SQLAlchemyError as e:
            db.rollback()
            return jsonify({'error': str(e), 'message': 'Failed to create token'}), 500

        except Exception as e:
            return jsonify({'error': str(e), 'message': 'An unexpected error occurred'}), 500

    @staticmethod
    def get_tokens():
        db = next(get_bd())

        try:
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

        except SQLAlchemyError as e:
            db.rollback()
            return jsonify({'error': str(e), 'message': 'Failed to get tokens'}), 500

        except Exception as e:
            return jsonify({'error': str(e), 'message': 'An unexpected error occurred'}), 500

    @staticmethod
    def update_token_expiry(data):
        db = next(get_bd())

        try:
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

        except SQLAlchemyError as e:
            db.rollback()
            return jsonify({'error': str(e), 'message': 'Failed to update token expiry'}), 500

        except Exception as e:
            return jsonify({'error': str(e), 'message': 'An unexpected error occurred'}), 500

    @staticmethod
    def delete_expired_token():
        db = next(get_bd())

        try:
            db.query(
                RegistrationToken).filter(
                RegistrationToken.expiry_date < datetime.datetime.utcnow()
            ).delete(synchronize_session=False)# вроде ускоряет массовые операции
            # а если учесть непоредленное число токенов, то думаю это просто тут необходимо

            db.commit()

            return jsonify({
                'message': 'All expired Token delete',
                "data": {}
            }), 200

        except SQLAlchemyError as e:
            db.rollback()
            return jsonify({'error': str(e), 'message': 'Failed to delete expired token'}), 500

        except Exception as e:
            return jsonify({'error': str(e), 'message': 'An unexpected error occurred'}), 500

    @staticmethod
    def delete_token(data):
        db = next(get_bd())

        try:
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

        except SQLAlchemyError as e:
            db.rollback()
            return jsonify({'error': str(e), 'message': 'Failed to delete token'}), 500

        except Exception as e:
            return jsonify({'error': str(e), 'message': 'An unexpected error occurred'}), 500

    @staticmethod
    def set_max_users(data):
        db = next(get_bd())

        try:
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

        except SQLAlchemyError as e:
            db.rollback()
            return jsonify({'error': str(e), 'message': 'Failed to set max users for token'}), 500

        except Exception as e:
            return jsonify({'error': str(e), 'message': 'An unexpected error occurred'}), 500

    @staticmethod
    def register_user(data):
        db = next(get_bd())

        try:
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

            new_user = User(
                regToken_id=reqToken.regToken_id,
                username=name,
                password=password
            )

            # Сохраняем нового пользователя в базу данных
            db.add(new_user)
            db.commit()

            return jsonify({
                'message': 'User registered successfully',
                "data": {
                    'user_name': new_user.username,
                    'user_id': new_user.user_id
                }
            }), 201

        except SQLAlchemyError as e:
            db.rollback()
            return jsonify({
                'error': 'Database error',
                'message': 'Failed to register new user.',
                'details': str(e)
            }), 500

        except ValueError as e:
            return jsonify({
                'error': 'Invalid data',
                'message': str(e)
            }), 400

        except Exception as e:
            return jsonify({
                'error': 'Unexpected error',
                'message': 'An unexpected error occurred.',
                'details': str(e)
            }), 500

    @staticmethod
    def login_user(data):
        pass


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
    return AuthService.register_user(data=request.get_json())


@auth_blueprint.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    print("/auth/login", data)
    return