from models import User
from extensions import db, bcrypt

class AuthService:

    @staticmethod
    def register(
        username,
        email,
        password,
        role
    ):

        existing = User.query.filter_by(
            email=email
        ).first()

        if existing:
            raise Exception(
                "Email already exists"
            )

        password_hash = bcrypt.generate_password_hash(
            password
        ).decode()

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def authenticate(
        email,
        password
    ):

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:
            return None

        if not bcrypt.check_password_hash(
            user.password_hash,
            password
        ):
            return None

        return user
