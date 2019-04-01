import datetime
import factory

from factory.fuzzy import BaseFuzzyDateTime

from reservationservice.app import db
from reservationservice.app.models import Reservation


class ReservationFactory(factory.alchemy.SQLAlchemyModelFactory, factory.Factory):

    class Meta:
        model = Reservation
        sqlalchemy_session = db.session

    create_date = BaseFuzzyDateTime(datetime.datetime(2017, 1, 1), datetime.datetime(2017, 12, 12))
    update_date = BaseFuzzyDateTime(datetime.datetime(2017, 1, 1), datetime.datetime(2017, 12, 12))
