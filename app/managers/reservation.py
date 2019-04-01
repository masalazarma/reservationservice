#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reservationservice.app.models import Reservation

class ReservationManager(object):
    """
    Contain methods to access to data related to Reservation Model
    """

    def __init__(self, auto_commit=True):
        """
        Autocommit and db session defaul values.
        For manage transactions auto_commit should be equal = False
        :param auto_commit: Boolean, auto commit (Transactions auto_commit = False)
        """

        self.auto_commit = auto_commit
        self.db_session = db.session

    @classmethod
    def get(self, filters):
        """
        Get first reservation match with filters
        :param filters: Dictionary, filters of itme wants to get. Ie {'id': '2h-34-jh-34'}
        :returns Reservation item object that mathc with the filters
        """
        try:
            reservation =  self.db_session.query(Reservation).filter_by(**filters).first()
            if not reservation:
                return None

            return reservation

        except Exception, e:
            error_message = "Error getting reservation by filters {0}. Detail error {1}".format(filters, e.message)
            print error_message
            return None

    @classmethod
    def create(self, data):
        """
        create reservation item
        :param data: Dictionary with the data to create. Ie {'user_id': 34, 'event_id': 45}
        """
        try:
            attributes_to_create = ('user_id', 'event_id')
            create_dict = {}

            for attribute in attributes_to_create:
                create_dict[attribute] = data[attribute]

            reservation = Reservation(**create_dict)

            self.db_session.add(reservation)
            self.db_session.flush()

            if self.auto_commit:
                self.db_session.commit()

            return reservation

        except Exception, e:
            error_message = "Error creating reservation by data {0}. Detail error {1}".format(data, e.message)
            print error_message
            return None

    @classmethod
    def select(self, filters):
        """
        Get all reservation match with filters
        :param filters: Dictionary, filters of itme wants to get. Ie {'use_id': '45'}
        :returns list with Reservation item object that mathc with the filters
        """
        try:
            reservations =  self.db_session.query(Reservation).filter_by(**filters).all()

            return reservations

        except Exception, e:
            error_message = "Error getting reservations by filters {0}. Detail error {1}".format(filters, e.message)
            print error_message
            return []
