from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from models import Doctor
from extensions import db

doctors_bp = Blueprint(
    "doctors",
    __name__
)

@doctors_bp.route("/doctors", methods=["POST"])
@jwt_required()
def create_doctor():

    data = request.get_json()

    doctor = Doctor(**data)

    db.session.add(doctor)
    db.session.commit()

    return jsonify(
        {"message": "Doctor Added"}
    )
