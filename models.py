from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        nullable=False
    )

class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(30))
    medical_history = db.Column(db.Text)

class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120))
    department = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    experience = db.Column(db.Integer)
    contact_info = db.Column(db.String(255))

class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id")
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id")
    )

    appointment_time = db.Column(
        db.DateTime,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="Scheduled"
    )

class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id")
    )

    amount = db.Column(db.Float)
    status = db.Column(db.String(50))

class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)

    product_name = db.Column(db.String(120))
    quantity = db.Column(db.Integer)
    supplier = db.Column(db.String(120))
    expiry_date = db.Column(db.Date)

class MedicalRecord(db.Model):
    __tablename__ = "medical_records"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id")
    )

    file_path = db.Column(db.String(255))

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
