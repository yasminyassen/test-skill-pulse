from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from models import User
from extensions import db, bcrypt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    hashed = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=hashed,
        role=data.get("role", "Receptionist")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User Created"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    user = User.query.filter_by(
        email=data["email"]
    ).first()

    if not user:
        return jsonify({"error": "Invalid Credentials"}), 401

    if not bcrypt.check_password_hash(
        user.password_hash,
        data["password"]
    ):
        return jsonify({"error": "Invalid Credentials"}), 401

    token = create_access_token(
        identity=user.id
    )

    return jsonify(
        access_token=token
    )
