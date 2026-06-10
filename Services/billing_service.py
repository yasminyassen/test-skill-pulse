from models import Invoice
from models import Payment

from extensions import db

class BillingService:

    @staticmethod
    def create_invoice(
        patient_id,
        amount
    ):

        invoice = Invoice(
            patient_id=patient_id,
            amount=amount,
            status="Pending"
        )

        db.session.add(invoice)

        db.session.commit()

        return invoice

    @staticmethod
    def record_payment(
        invoice_id,
        amount,
        method
    ):

        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            payment_method=method
        )

        invoice = Invoice.query.get(
            invoice_id
        )

        invoice.status = "Paid"

        db.session.add(payment)

        db.session.commit()

        return payment
