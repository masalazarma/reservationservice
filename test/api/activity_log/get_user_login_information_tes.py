from mock.mock import patch

from general.auth.user import User
from general.exception.errors import deserialize_json
from general.test.data.user_data import get_user_data
from general.util.test_helper import TestHttpRequest
from general.util.test_helper import BaseTest

from userservice.app import db as user_service_db
from userservice.app import api, auth
from userservice.default_config import basedir as userservice_basedir
from userservice.app.factories.factories import ActivityLogFactory


class GetUserLoginInformationTest(BaseTest):
    """
    Set of tests for login-information endpoint
    """

    client_id = 11
    user_test = get_user_data(client_id)
    user_test['email'] = 'test@email.com'

    @classmethod
    def setUpClass(cls):

        cls.__endpoint_url = '/userservice/api/v1.0/login-information'

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

    def test_unauthorized_error(self):
        """
        Check the endpoint returns a 401 if no token is provided
        """
        response = self.http_request.get()
        self.response_code_assert(401, response)

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_approval_limit_by_cient_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Check the endpoint return correct login information
        """

        user = User(self.user_test)
        mock_request_ctx_stack.top.current_user = user

        ActivityLogFactory.create(client_id=self.client_id, user_name=self.user_test['email'], event_type='USER LOGIN')
        ActivityLogFactory.create(client_id=self.client_id, user_name=self.user_test['email'], event_type='USER LOGIN')
        ActivityLogFactory.create(client_id=self.client_id, user_name=self.user_test['email'], event_type='USER LOGIN')
        ActivityLogFactory.create(client_id=self.client_id, user_name=self.user_test['email'], event_type='USER LOGIN')
        ActivityLogFactory.create(client_id=self.client_id, user_name=self.user_test['email'], event_type='USER CREATED')
        user_service_db.session.commit()
        data = {
                'email': self.user_test['email']
            }

        response = self.http_request.get(data)
        response_data = deserialize_json(response.data)

        self.json_structure_response_code_assert(200, response)
        self.assertIn('data', response_data)

        login_information = response_data['data']
        self.assertEqual(login_information['email'], self.user_test['email'])
        self.assertEqual(login_information['login_count'], 4)
        self.assertIn('last_login_date', login_information)
