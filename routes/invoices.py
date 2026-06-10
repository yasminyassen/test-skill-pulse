from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from models import Invoice
from extensions import db

invoice_bp = Blueprint(
    "invoice",
    __name__
)

@invoice_bp.route(
    "/invoices",
    methods=["POST"]
)
@jwt_required()
def create_invoice():

    data = request.get_json()

    invoice = Invoice(**data)

    db.session.add(invoice)
    db.session.commit()

    return jsonify(
        {"message": "Invoice Created"}
    )
