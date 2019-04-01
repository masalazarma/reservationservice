#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from mock.mock import MagicMock, Mock
import unittest
from contextlib import nested

from general.util.test_helper import BaseTest

from reservationservice.app.controllers.reservation import ReservationController
from reservationservice.app.factories.factories import ReservationFactory
from reservationservice.default_config import basedir as reservation_basedir
from reservationservice.app import db as reservationservice_db
from reservationservice.app import app


class CreateReservationTest(BaseTest):
    """
    Set of tests for create_reservation in ReservationController
    """

    reservation = {
        'user_id': 20, 'event_id':35
    }

    def setUp(cls):
        application_databases = {
            'reservationservice': {
                'base_directory': reservation_basedir,
                'db_instance': reservationservice_db
            }
        }

        cls.set_up_db(application_databases, create_files=False)

    def test_create_reservation_successful(self):
        """
        Check if creates reservation and return successfully data
        """

        with nested(*self.build_patches({})):
            response = ReservationController().create_reservation(self.reservation)

            self.assertEqual(response['user_id'], self.reservation['user_id'])
            self.assertEqual(response['event_id'], self.reservation['event_id'])
