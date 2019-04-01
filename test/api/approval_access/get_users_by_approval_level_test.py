from mock.mock import patch

from general.auth.user import User
from general.exception.errors import deserialize_json
from general.test.data.user_data import get_user_data
from general.util.test_helper import TestHttpRequest
from general.util.test_helper import BaseTest

from userservice.app import db as user_service_db
from userservice.app import api, auth
from userservice.default_config import basedir as userservice_basedir
from userservice.app.factories.factories import ApprovalAccessFactory, ApprovalLimitFactory, UserFactory


class GetUsersByApprovalLevelTest(BaseTest):
    """
    Set of tests for approval-access/<int:approval_level> endpoint
    """

    client_id = 11
    approval_level = 2
    user_test = get_user_data(client_id)

    @classmethod
    def setUpClass(cls):

        cls.__endpoint_url = '/userservice/api/v1.0/approval-access/{0}'.format(cls.approval_level)

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
    def test_users_by_approval_level_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Check the endpoint that return a list of users from an approvel level id
        """
        user = User(self.user_test)
        mock_request_ctx_stack.top.current_user = user

        UserFactory.create(
            client_id=self.client_id,
            id=user.id
        )
        second_user = UserFactory.create(
            client_id=self.client_id,
            id=10
        )

        approval_limit = ApprovalLimitFactory.create(
            client_id=self.client_id,
            amount=10000,
            level=self.approval_level
        )
        user_service_db.session.commit()

        ApprovalAccessFactory.create(
            user_id=user.id,
            approval_limit=approval_limit
        )
        ApprovalAccessFactory.create(
            user_id=second_user.id,
            approval_limit=approval_limit
        )

        user_service_db.session.commit()

        users_ids = [second_user.id, user.id]

        response = self.http_request.get()
        response_data = deserialize_json(response.data)

        self.json_structure_response_code_assert(200, response)

        self.assertIn('data', response_data)

        users_list = response_data['data']

        self.assertEqual(len(users_list), 2)

        for user in users_list:
            self.assertIn(user['user_id'], users_ids)
            self.assertEqual(self.client_id, user['client_id'])

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_users_by_approval_level_not_existent_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Check the endpoint that return a list of users from an approvel level id
        """
        user = User(self.user_test)
        mock_request_ctx_stack.top.current_user = user

        UserFactory.create(
            client_id=self.client_id,
            id=user.id
        )
        second_user = UserFactory.create(
            client_id=self.client_id,
            id=10
        )

        approval_limit = ApprovalLimitFactory.create(
            client_id=self.client_id,
            amount=10000,
            level=1
        )
        user_service_db.session.commit()

        ApprovalAccessFactory.create(
            user_id=user.id,
            approval_limit=approval_limit
        )
        ApprovalAccessFactory.create(
            user_id=second_user.id,
            approval_limit=approval_limit
        )

        user_service_db.session.commit()

        users_ids = [second_user.id, user.id]

        response = self.http_request.get()
        response_data = deserialize_json(response.data)

        self.json_structure_response_code_assert(200, response)

        self.assertIn('data', response_data)

        users_list = response_data['data']

        self.assertEqual(len(users_list), 0)
