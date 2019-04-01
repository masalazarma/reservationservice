#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import nested

from mock import Mock
from werkzeug.security import generate_password_hash

from general.mock.general.util.user_service_property_helper_mock import UserServicePropertyHelperMock
from general.test.data.user_data import get_user_data

from userservice.app.api import app

from general.mock.general.util.lending_portal_property_helper_mock import LendingPortalPropertyHelperMock
from general.util.test_helper import BaseTest
from userservice.app import db as user_service_db
from userservice.app.controllers.password_history import PasswordHistoryController
from userservice.default_config import basedir as userservice_basedir


class ValidatePasswordHistoryTest(BaseTest):

    client_id = 20
    user_test = get_user_data(client_id)

    """
    Set of tests for validate password history method in PasswordHistoryController
    """

    @classmethod
    def setUpClass(cls):

        # So the exception would be catch by flask-restful
        app.config['PROPAGATE_EXCEPTIONS'] = False
        cls.app = app.test_client()

    def setUp(cls):
        application_databases = {
            'userservice': {
                'base_directory': userservice_basedir,
                'db_instance': user_service_db
            }
        }
        cls.set_up_db(application_databases, create_files=False)

    def get_patches(self):
        lending_property_helper_mock = LendingPortalPropertyHelperMock()
        user_property_helper_mock = UserServicePropertyHelperMock()
        lending_property_helper_mock.get_password_expired_days = Mock(return_value=1)
        patch_dict = {
            'userservice.app.controllers.password_history.LendingPortalPropertyHelper': {
                'return_value': lending_property_helper_mock
            },
            'userservice.app.controllers.password_history.UserServicePropertyHelper': {
                'return_value': user_property_helper_mock
            }
        }
        return patch_dict

    def test_validate_password_history_success(self):
        """
        Validate password history success
        """
        with nested(*self.build_patches(self.get_patches())):
            password = "pass1234!"
            password_hash = generate_password_hash(password)
            result = PasswordHistoryController.validate_password_history(
                client_id=20,
                user_id=1,
                password=password_hash)
            self.assertEqual(result, True)
            PasswordHistoryController.create_password_history(client_id=20, user_id=1, password=password_hash)
            result = PasswordHistoryController.validate_password_history(
                client_id=20, user_id=1, password=password)
            self.assertEqual(result, False)
            password = "pass1234!1"
            result = PasswordHistoryController.validate_password_history(
                client_id=20, user_id=1, password=password)
            self.assertEqual(result, True)
