#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from mock.mock import MagicMock, Mock
import unittest
from contextlib import nested

from general.util.test_helper import BaseTest

from userservice.app.controllers.user import UserController
from userservice.app.factories.factories import UserFactory
from userservice.default_config import basedir as userservice_basedir
from userservice.app import db as user_service_db
from userservice.app import app


class userExistsTest(BaseTest):

    client_id = 11
    email = 'test@lendingfront.com'
    roles = [{'name': 'PARTNER'}, {'name': 'PARTNER_TEAM_VIEW'}]

    """
    Set of tests for get_user_exists in UserController
    """

    def setUp(cls):
        application_databases = {
            'userservice': {
                'base_directory': userservice_basedir,
                'db_instance': user_service_db
            }
        }

        cls.set_up_db(application_databases, create_files=False)

    def test_user_exist_successful(self):
        """
        Check that the user exist and return data successfully
        """

        patch_dict = {
            'userservice.app.controllers.user.ClientRoleController.get_user_or_client_roles': {
                'return_value': self.roles
            },
        }

        with nested(*self.build_patches(patch_dict)):
            user = UserFactory.create(
                id=20,
                client_id=self.client_id,
                user_status='ACTIVE',
                email=self.email
            )
            user_service_db.session.commit()

            response = UserController.get_user_exist({'email': self.email})

            self.assertIsNotNone(response)

            self.assertIn('user_id', response)
            self.assertEqual(response['user_id'], 20)

            self.assertIn('roles', response)
            self.assertEqual(response['roles'], ['PARTNER', 'PARTNER_TEAM_VIEW'])

            self.assertIn('user_exists', response)
            self.assertTrue(response['user_exists'])

    def test_user_not_exist_successful(self):
        """
        Check the user not exist and responce is expectedone
        """

        patch_dict = {
            'userservice.app.controllers.user.ClientRoleController.get_user_or_client_roles': {
                'return_value': self.roles
            },
        }

        with nested(*self.build_patches(patch_dict)):
            user = UserFactory.create(
                id=20,
                client_id=self.client_id,
                user_status='ACTIVE',
                email=self.email
            )
            user_service_db.session.commit()

            response = UserController.get_user_exist({'email': 'other@email.com'})

            self.assertIsNotNone(response)

            self.assertIn('user_id', response)
            self.assertEqual(response['user_id'], None)

            self.assertIn('roles', response)
            self.assertEqual(response['roles'], [])

            self.assertIn('user_exists', response)
            self.assertFalse(response['user_exists'])
