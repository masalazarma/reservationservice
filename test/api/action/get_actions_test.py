from mock.mock import patch

from general.auth.user import User
from general.exception.errors import deserialize_json
from general.util.dict_helper import merge_two_dicts
from general.util.test_helper import TestHttpRequest, TestInMemoryDatabaseMixin, TestMockMixin, BaseTest
from general.test.data.user_data import get_user_data

from userservice.app import db as user_service_db
from userservice.app import api, auth
from userservice.default_config import basedir as userservice_basedir
from userservice.app.factories.factories import ActionFactory, ClientActionFactory


class GetActionsTest(BaseTest):

    client_id = 3
    user_test = get_user_data(client_id)

    """
    Set of tests for GET /userservice/api/v1.0/actions endpoint
    """

    @classmethod
    def setUpClass(cls):
        cls.__endpoint_url = '/userservice/api/v1.0/actions'

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

    def unauthorized_test(self):
        """
        Check jwt is requesting Authorization Bearer
        """

        response = self.http_request.get()
        self.response_code_assert(401, response)

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def get_actions_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Checking correct data trying to get_actions
        """

        # TODO: find a way to implement this in a function once
        mock_request_ctx_stack.top.current_user = User(self.user_test)
        action = ActionFactory(id=5, name='FULL_ACCESS', category='AMINISTRATOR')
        ClientActionFactory(client_id=self.client_id, action_id=action.id, status="ACTIVE")
        user_service_db.session.commit()

        response = self.http_request.get()
        self.verify_success_response(response, action)

    def verify_success_response(self, response, action):
        self.response_code_assert(200, response)
        response_data = deserialize_json(response.data)
        self.assertEqual(action.name, response_data['actions'][0]['name'])
        self.assertEqual(action.category, response_data['actions'][0]['category'])
