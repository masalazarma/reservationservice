from mock.mock import patch
from mock import Mock
from contextlib import nested

from general.auth.user import User
from general.exception.errors import deserialize_json
from general.test.data.user_data import get_user_data
from general.util.test_helper import TestHttpRequest
from general.util.test_helper import BaseTest

from userservice.app import db as user_service_db
from userservice.app import api, auth
from userservice.default_config import basedir as userservice_basedir
from userservice.app.factories.factories import UserFactory
from userservice.app.models import User as userModel


class AuthenticateUserTest(BaseTest):
    """
    Set of tests for user authenticate endpoint
    """

    client_id = 11
    user_test = get_user_data(client_id)

    @classmethod
    def setUpClass(cls):

        cls.__endpoint_url = '/userservice/api/v1.0/authenticate'

        # So the exception would be catch by flask-restful
        api.app.config['PROPAGATE_EXCEPTIONS'] = False
        cls.app = api.app.test_client()

        cls.http_request = TestHttpRequest(cls.app, cls.__endpoint_url)

    def setUp(cls):
        application_databases = {
            'userservice': {
                'base_directory': userservice_basedir,
                'db_instance': user_service_db
            }
        }

        cls.set_up_db(application_databases, create_files=False)

    def get_patches(self, new_patches=None):
        """
        Define and load patches to mock the calls
        """
        patch_dict = {}

        if new_patches is not None:
            for key, value in new_patches.iteritems():
                patch_dict[key] = value

        return self.build_patches(patch_dict)

    def test_authentication_fail_user_not_found_success(self):
        """
        Check the endpoint returns an error message because the user was not found
        """

        with nested(*self.get_patches()):

            data = {
                'username': 'test@email.com',
                'password': '12345'
            }

            response = self.http_request.post(data)
            response_data = deserialize_json(response.data)
            self.json_structure_response_code_assert(400, response)

            self.assertIn('status', response_data)
            self.assertIn('message', response_data)

            self.assertEqual('ERROR', response_data['status'])
            self.assertEqual('Incorrect user credentials.', response_data['message'])
