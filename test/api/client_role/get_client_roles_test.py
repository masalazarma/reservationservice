from mock.mock import patch

from general.auth.user import User
from general.exception.errors import deserialize_json
from general.util.dict_helper import merge_two_dicts
from general.util.test_helper import TestHttpRequest, BaseTest
from general.test.data.user_data import get_user_data

from userservice.app import db as user_service_db
from userservice.app import api, auth
from userservice.default_config import basedir as userservice_basedir
from userservice.app.factories.factories import UserFactory, ClientRoleFactory


class GetClientRolesTest(BaseTest):

    client_id = 3
    user_test = get_user_data(client_id)

    """
    Set of tests for GET /userservice/api/v1.0/user/client_roles endpoint
    """

    @classmethod
    def setUpClass(cls):
        cls.__endpoint_url = '/userservice/api/v1.0/user/client_roles'

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
    def no_data_error_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Checking correct error code trying to get_client_roles without data
        """

        # TODO: find a way to implement this in a function once
        mock_request_ctx_stack.top.current_user = User(self.user_test)

        response = self.http_request.get()
        self.json_error_response_assert(response, 400)

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def user_client_roles_success_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Checking correct success code trying to get_client_roles by user_id
        """

        data = {
            'client_id': self.client_id,
            'user_id': self.user_test['user_id'],
            'roles_names': []
        }

        # TODO: find a way to implement this in a function once
        mock_request_ctx_stack.top.current_user = User(self.user_test)

        user = UserFactory.create(client_id=self.client_id)
        client_role = ClientRoleFactory.create_batch(3, client_id=self.client_id)
        user.client_roles = client_role

        user_service_db.session.commit()

        response = self.http_request.get(data)
        response_data = deserialize_json(response.data)

        self.json_structure_response_code_assert(200, response)
        self.assertTrue('roles' in response_data)
        self.assertEquals(3, len(response_data['roles']))

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def client_roles_success_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Checking correct success code trying to get_client_roles by client_id
        """

        data = {
            'client_id': self.client_id,
            'user_id': None,
            'roles_names': []
        }

        # TODO: find a way to implement this in a function once
        mock_request_ctx_stack.top.current_user = User(self.user_test)

        ClientRoleFactory.create_batch(3, client_id=self.client_id)
        user_service_db.session.commit()

        response = self.http_request.get(data)
        response_data = deserialize_json(response.data)

        self.json_structure_response_code_assert(200, response)
        self.assertTrue('roles' in response_data)
        self.assertEquals(3, len(response_data['roles']))

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def not_filter_by_name_client_roles_success_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Checking correct success code trying to get_client_roles by
        client_id and not filtering by roles names list
        """

        data = {
            'client_id': self.client_id,
            'user_id': None,
            'roles_names': []
        }

        # TODO: find a way to implement this in a function once
        mock_request_ctx_stack.top.current_user = User(self.user_test)

        ClientRoleFactory.create_batch(3, client_id=self.client_id)
        ClientRoleFactory.create(client_id=self.client_id, name='API')
        user_service_db.session.commit()

        response = self.http_request.get(data)
        response_data = deserialize_json(response.data)

        self.json_structure_response_code_assert(200, response)
        self.assertTrue('roles' in response_data)
        self.assertEquals(4, len(response_data['roles']))

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def filter_by_name_client_roles_success_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Checking correct success code trying to get_client_roles by
        client_id and filtering by roles names list
        """

        data = {
            'client_id': self.client_id,
            'user_id': None,
            'roles_names': ['API']
        }

        # TODO: find a way to implement this in a function once
        mock_request_ctx_stack.top.current_user = User(self.user_test)

        ClientRoleFactory.create_batch(3, client_id=self.client_id)
        ClientRoleFactory.create(client_id=self.client_id, name='API')
        user_service_db.session.commit()

        response = self.http_request.get(data)
        response_data = deserialize_json(response.data)

        self.json_structure_response_code_assert(200, response)
        self.assertTrue('roles' in response_data)
        self.assertEquals(3, len(response_data['roles']))

        for role in response_data['roles']:
            self.assertTrue('name' in role)
            self.assertTrue('API' != role['name'])
