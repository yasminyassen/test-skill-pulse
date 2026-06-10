from models import Doctor
from extensions import db

class DoctorService:

    @staticmethod
    def create_doctor(data):

        doctor = Doctor(**data)

        db.session.add(doctor)
        db.session.commit()

        return doctor

    @staticmethod
    def assign_specialization(
        doctor_id,
        specialization
    ):

        doctor = Doctor.query.get(
            doctor_id
        )

        if not doctor:
            raise Exception(
                "Doctor not found"
            )

        doctor.specialization = (
            specialization
        )

        db.session.commit()

        return doctor
