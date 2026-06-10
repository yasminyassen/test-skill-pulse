from datetime import datetime

from models import Appointment
from extensions import db

class AppointmentService:

    @staticmethod
    def book(
        patient_id,
        doctor_id,
        appointment_time
    ):

        conflict = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_time=appointment_time
        ).first()

        if conflict:
            raise Exception(
                "Time slot unavailable"
            )

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_time=appointment_time,
            status="Scheduled"
        )

        db.session.add(
            appointment
        )

        db.session.commit()

        return appointment

    @staticmethod
    def cancel(
        appointment_id
    ):

        appointment = Appointment.query.get(
            appointment_id
        )

        if not appointment:
            raise Exception(
                "Appointment not found"
            )

        appointment.status = (
            "Cancelled"
        )

        db.session.commit()

        return appointment

    @staticmethod
    def reschedule(
        appointment_id,
        new_time
    ):

        appointment = Appointment.query.get(
            appointment_id
        )

        if not appointment:
            raise Exception(
                "Appointment not found"
            )

        appointment.appointment_time = (
            new_time
        )

        appointment.status = (
            "Rescheduled"
        )

        db.session.commit()

        return appointment
