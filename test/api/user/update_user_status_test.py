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


class UpdateUserStatusTest(BaseTest):
    """
    Set of tests for user status endpoint
    """

    client_id = 11
    user_test = get_user_data(client_id)

    @classmethod
    def setUpClass(cls):

        cls.__endpoint_url = '/userservice/api/v1.0/user/status'

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
        patch_dict = {
            'userservice.app.user.log_event': {
                'return_value': None
            },
        }

        if new_patches is not None:
            for key, value in new_patches.iteritems():
                patch_dict[key] = value

        return self.build_patches(patch_dict)

    def test_unauthorized_error(self):
        """
        Check the endpoint returns a 401 if no token is provided
        """
        response = self.http_request.post()
        self.response_code_assert(401, response)

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_update_user_status_inactive_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Check the endpoint update user status to INACTIVE
        """
        with nested(*self.get_patches()):
            user_test = self.user_test
            user_test['email'] = 'test@lendingfront.com'
            mock_request_ctx_stack.top.current_user = User(user_test)
            user_id = 20
            UserFactory.create(
                id=user_id,
                client_id=self.client_id,
                user_status='ACTIVE'
            )
            user_service_db.session.commit()

            data = {
                'user_id': user_id,
                'client_id': self.client_id
            }

            response = self.http_request.post(data)

            self.json_structure_response_code_assert(200, response)

            user_updated = user_service_db.session.query(userModel).filter(
                userModel.id == user_id, userModel.client_id == self.client_id
            ).first()

            self.assertEqual('INACTIVE', user_updated.user_status)

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_update_user_status_active_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Check the endpoint update user status to ACTIVE
        """
        with nested(*self.get_patches()):
            user_test = self.user_test
            user_test['email'] = 'test@lendingfront.com'
            mock_request_ctx_stack.top.current_user = User(user_test)
            user_id = 20
            UserFactory.create(
                id=user_id,
                client_id=self.client_id,
                user_status='INACTIVE'
            )
            user_service_db.session.commit()

            data = {
                'user_id': user_id,
                'client_id': self.client_id
            }

            response = self.http_request.post(data)

            self.json_structure_response_code_assert(200, response)

            user_updated = user_service_db.session.query(userModel).filter(
                userModel.id == user_id, userModel.client_id == self.client_id
            ).first()

            self.assertEqual('ACTIVE', user_updated.user_status)

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_update_user_status_not_found_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Check the endpoint return an error that the user was not found
        """
        with nested(*self.get_patches()):
            user_test = self.user_test
            user_test['email'] = 'test@lendingfront.com'
            mock_request_ctx_stack.top.current_user = User(user_test)
            user_id = 20

            data = {
                'user_id': user_id,
                'client_id': self.client_id
            }

            response = self.http_request.post(data)

            self.json_structure_response_code_assert(200, response)

            response_data = deserialize_json(response.data)

            self.assertEqual(response_data['status'], "ERROR")
            self.assertEqual(response_data['message'], "User not found")
