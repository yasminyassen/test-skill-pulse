from models import Patient
from extensions import db

class PatientService:

    @staticmethod
    def create_patient(data):

        patient = Patient(**data)

        db.session.add(patient)
        db.session.commit()

        return patient

    @staticmethod
    def update_patient(
        patient_id,
        data
    ):

        patient = Patient.query.get(
            patient_id
        )

        if not patient:
            raise Exception(
                "Patient not found"
            )

        for key, value in data.items():
            setattr(
                patient,
                key,
                value
            )

        db.session.commit()

        return patient

    @staticmethod
    def delete_patient(
        patient_id
    ):

        patient = Patient.query.get(
            patient_id
        )

        if not patient:
            raise Exception(
                "Patient not found"
            )

        db.session.delete(patient)

        db.session.commit()

    @staticmethod
    def search_patient(
        keyword
    ):

        return Patient.query.filter(
            Patient.name.ilike(
                f"%{keyword}%"
            )
        ).all()
