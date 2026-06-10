from models import Medicine
from extensions import db

class InventoryService:

    @staticmethod
    def add_medicine(data):

        medicine = Medicine(**data)

        db.session.add(medicine)

        db.session.commit()

        return medicine

    @staticmethod
    def update_stock(
        medicine_id,
        quantity
    ):

        medicine = Medicine.query.get(
            medicine_id
        )

        if not medicine:
            raise Exception(
                "Medicine not found"
            )

        medicine.quantity = quantity

        db.session.commit()

        return medicine

    @staticmethod
    def get_low_stock():

        return Medicine.query.filter(
            Medicine.quantity < 10
        ).all()
