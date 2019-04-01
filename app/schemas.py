from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

from reservationservice.app.models import Reservation

class ReservationShema(ModelSchema):
    """
    Serialize Reservation model
    """

    class Meta:
        model = Reservation

    create_date = fields.Method("get_create_date", dump_only=True)
    update_date = fields.Method("get_update_date", dump_only=True)

    def get_create_date(self, reservation):
        return reservation.create_date.strftime("%m/%d/%Y")

    def get_update_date(self, reservation):
        return reservation.update_date.strftime("%m/%d/%Y")
