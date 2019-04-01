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


class UserCustomerResendInvitationTest(BaseTest):
    """
    Set of tests for resend-user-customer-invitation endpoint
    """

    client_id = 11
    user_test = get_user_data(client_id)

    @classmethod
    def setUpClass(cls):

        cls.__endpoint_url = '/userservice/api/v1.0/user/customer/resend-invitation'

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
            'userservice.app.controllers.user.user_creation_notification': {
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
        response = self.http_request.put()
        self.response_code_assert(401, response)

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_resend_customer_invitation_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Check the endpoint that resend a customer invitation email and update the password
        """

        user_creation_notification = Mock()

        new_patches = {
            'userservice.app.controllers.user.user_creation_notification': {
                'new': user_creation_notification
            },
        }

        with nested(*self.get_patches(new_patches)):

            mock_request_ctx_stack.top.current_user = User(self.user_test)
            user_id = 20
            user = UserFactory.create(
                id=20,
                client_id=self.client_id,
                password='abc123'
            )
            user_service_db.session.commit()
            user_object = user.__dict__

            data = {
                'user_id': user_id
            }

            response = self.http_request.put(data)

            self.json_structure_response_code_assert(200, response)

            user_creation_notification.assert_called()

            user_updated = user_service_db.session.query(userModel).filter(
                userModel.id == user_id, userModel.client_id == self.client_id
            ).first()

            self.assertTrue(user_updated.change_password_flag)
            self.assertFalse(user_updated.verify_password(user_object['password_hash']))

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_resend_invitation_user_not_found_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Check the endpoint that resend a customer invitation email return an error about user not found
        """

        user_creation_notification = Mock()

        new_patches = {
            'userservice.app.controllers.user.user_creation_notification': {
                'new': user_creation_notification
            },
        }

        with nested(*self.get_patches(new_patches)):
            mock_request_ctx_stack.top.current_user = User(self.user_test)
            user_id = 20
            user = UserFactory.create(
                id=20,
                client_id=4,
                password='abc123'
            )
            user_service_db.session.commit()

            data = {
                'user_id': user_id
            }

            response = self.http_request.put(data)
            response_data = deserialize_json(response.data)

            self.json_structure_response_code_assert(400, response)

            self.assertEqual(response_data['message'], 'User not found')
            self.assertEqual(response_data['error_code'], '02')
