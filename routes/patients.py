from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from models import Patient
from extensions import db

patients_bp = Blueprint(
    "patients",
    __name__
)

@patients_bp.route("/patients", methods=["GET"])
@jwt_required()
def get_patients():

    patients = Patient.query.all()

    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "phone": p.phone
        }
        for p in patients
    ])


@patients_bp.route("/patients", methods=["POST"])
@jwt_required()
def create_patient():

    data = request.get_json()

    patient = Patient(**data)

    db.session.add(patient)
    db.session.commit()

    return jsonify(
        {"message": "Patient Created"}
    ), 201
