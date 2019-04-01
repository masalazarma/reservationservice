#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reservationservice.app.resources import ReservationManager
from reservationservice.app.schemas import ReservationShema

class ReservationController(object):
    """
    Contain methods to access to data related to Reservation Model
    """

    def __init__(self):
        """
        Autocommit and db session defaul values.
        For manage transactions auto_commit should be equal = False
        :param auto_commit: Boolean, auto commit (Transactions auto_commit = False)
        """
        self.manager = ReservationManager()
        reservation_fields = ['id', 'user_id', 'event_id', 'create_date']
        self.schema_one = ReservationShema(many=False, only=reservation_fields)
        self.schema_many = ReservationShema(many=True, only=reservation_fields)

    @classmethod
    def get_reservation(self, reservation_id):
        """
        Get reservation by id
        :param reservation_id: Int, reservation id. Ie 45
        :returns dict item with reservation item
        """

        reservation = self.manager.get({'id': reservation_id})
        return self.schema_one.dump(reservation).data

    @classmethod
    def select_reservation(self, data):
        """
        Get reservation by id
        :param data: Dict, data to get reservations. Ie {'user_id': 24, 'event_id': 45}
        :returns list of items match with filters data
        """

        reservations = self.manager.select(data)
        return self.schema_many.dump(reservations).data

    @classmethod
    def create(self, data):
        """
        create reservation item
        :param data: Dictionary with the data to create. Ie {'user_id': 34, 'event_id': 45}
        """

        reservation = self.manager.create(data)
        return self.schema_one.dump(reservation).data
