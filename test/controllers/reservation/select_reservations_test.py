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


class SelectReservationTest(BaseTest):
    """
    Set of tests for select_reservation in ReservationController
    """

    def setUp(cls):
        application_databases = {
            'reservationservice': {
                'base_directory': reservation_basedir,
                'db_instance': reservationservice_db
            }
        }

        cls.set_up_db(application_databases, create_files=False)

    def test_get_reservations_by_user_id_successful(self):
        """
        Check if reservations are returned successfully by user
        """

        with nested(*self.build_patches({})):
            ReservationFactory.create(user_id=10, event_id=15)
            ReservationFactory.create(user_id=10, event_id=16)
            ReservationFactory.create(user_id=10, event_id=17)
            ReservationFactory.create(user_id=12, event_id=17)
            ReservationFactory.create(user_id=21, event_id=15)
            ReservationFactory.create(user_id=36, event_id=17)

            response = ReservationController().select_reservation({'user_id': 10})

            self.assertEqual(len(response), 3)
            for reservation in response:
                self.assertEqual(reservation['user_id'], 10)
                self.assertIn(reservation['event_id'], [15,16,17])

    def test_get_reservations_by_event_id_successful(self):
        """
        Check if reservations are returned successfully by event
        """

        with nested(*self.build_patches({})):
            ReservationFactory.create(user_id=10, event_id=15)
            ReservationFactory.create(user_id=10, event_id=16)
            ReservationFactory.create(user_id=10, event_id=17)
            ReservationFactory.create(user_id=12, event_id=17)
            ReservationFactory.create(user_id=21, event_id=15)
            ReservationFactory.create(user_id=36, event_id=17)

            response = ReservationController().select_reservation({'event_id': 17})

            self.assertEqual(len(response), 3)
            for reservation in response:
                self.assertEqual(reservation['event_id'], 17)
                self.assertIn(reservation['user_id'], [36,12,10])

    def test_get_reservations_by_user_id_and_event_id_successful(self):
        """
        Check if reservations are returned successfully by event and user
        """

        with nested(*self.build_patches({})):
            ReservationFactory.create(user_id=10, event_id=15)
            ReservationFactory.create(user_id=10, event_id=16)
            ReservationFactory.create(user_id=10, event_id=17)
            ReservationFactory.create(user_id=12, event_id=17)
            ReservationFactory.create(user_id=21, event_id=15)
            ReservationFactory.create(user_id=36, event_id=17)

            response = ReservationController().select_reservation({'user_id':36, 'event_id': 17})

            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['event_id'], 17)
            self.assertEqual(response[0]['user_id'], 36)
