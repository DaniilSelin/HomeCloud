from flask import Blueprint, request, jsonify
from models import RegistrationToken
from db import get_bd, engine
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
    def generate_token():
        # Логика генерации токена
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def register_user(data):
        pass

    @staticmethod
    def login_user(data):
        pass


# Создаем Blueprint
auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route("/auth/generate_token", methods=["POST"])
def generate_token():
    """Создает новый токен"""
    db = next(get_bd())

    try:
        data = request.get_json()

        expiry_days = data.get('expiry_days', 30)

        token = RegistrationToken(
            token=AuthService.generate_token(),
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


@auth_blueprint.route("/auth/get_tokens", methods=["GET"])
def get_tokens():
    """ Возвращает все токены"""
    db = next(get_bd())

    try:
        tokens = db.query(RegistrationToken).all()

        # Преобразуем объекты в словари для JSON сериализации
        tokens_list = [{
            'regToken_id': t.regToken_id,
            'token': t.token,
            'created_at': t.created_at.isoformat(),
            "expiry_date": t.expiry_date} for t in tokens]

        return jsonify({
            'message': 'Tokens retrieved successfully',
            "data": tokens_list
        }), 200

    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': str(e), 'message': 'Failed to get tokens'}), 500

    except Exception as e:
        return jsonify({'error': str(e), 'message': 'An unexpected error occurred'}), 500


@auth_blueprint.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    print("/auth/register", data)
    return


@auth_blueprint.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    print("/auth/login", data)
    return