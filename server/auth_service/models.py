from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_name = Column(String(24), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    regToken_id = Column(Integer, ForeignKey("RegistrationToken.regToken_id"))

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User(id(={self.user_id}, name=({self.user_name}))"


class RegistrationToken(Base):
    __tablename__ = "RegistrationToken"

    regToken_id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(36), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expiry_date = Column(DateTime, nullable=False)
    max_users = Column(Integer, default=1)

    def __init__(self, token, expiry_date=None, max_users=1):
        self.token = token
        if expiry_date is None:
            # Установите срок годности по умолчанию (например, через 30 дней)
            expiry_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        self.expiry_date = expiry_date
        self.max_users = max_users

    def __repr__(self):
        return f"Token(token={self.token}, created_at={self.created_at}, expiry_date={self.expiry_date}, max_users={self.max_users})"
