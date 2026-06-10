from models import Invoice
from models import Appointment
from models import Doctor

class ReportService:

    @staticmethod
    def revenue_report():

        invoices = Invoice.query.all()

        total = sum(
            x.amount
            for x in invoices
        )

        return {
            "total_revenue": total
        }

    @staticmethod
    def appointments_report():

        count = Appointment.query.count()

        return {
            "appointments": count
        }

    @staticmethod
    def doctor_performance():

        doctors = Doctor.query.all()

        report = []

        for doctor in doctors:

            total = Appointment.query.filter_by(
                doctor_id=doctor.id
            ).count()

            report.append({
                "doctor": doctor.name,
                "appointments": total
            })

        return report
