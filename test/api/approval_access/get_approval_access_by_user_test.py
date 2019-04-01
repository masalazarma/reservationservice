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


class GetApprovalAccessByUserTest(BaseTest):
    """
    Set of tests for approval-access endpoint
    """

    client_id = 11
    user_test = get_user_data(client_id)

    @classmethod
    def setUpClass(cls):

        cls.__endpoint_url = '/userservice/api/v1.0/approval-access'

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
    def test_approval_access_by_user_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Check the endpoint that return a list of approval access by an user
        """
        user = User(self.user_test)
        mock_request_ctx_stack.top.current_user = user

        UserFactory.create(id=user.id)
        second_user = UserFactory.create(id=10)

        first_approval_limit = ApprovalLimitFactory.create(
            client_id=self.client_id,
            amount=10000,
            level=1
        )
        second_approval_limit = ApprovalLimitFactory.create(
            client_id=self.client_id,
            amount=10000,
            level=2
        )
        user_service_db.session.commit()

        ApprovalAccessFactory.create(
            user_id=user.id,
            approval_limit=first_approval_limit
        )
        ApprovalAccessFactory.create(
            user_id=second_user.id,
            approval_limit=second_approval_limit
        )

        user_service_db.session.commit()

        first_approval_limit_object = first_approval_limit.__dict__

        response = self.http_request.get()
        response_data = deserialize_json(response.data)

        self.json_structure_response_code_assert(200, response)

        self.assertIn('data', response_data)

        approval_access_list = response_data['data']

        self.assertEqual(len(approval_access_list), 1)
        self.assertIn('approval_limit', approval_access_list[0])
        self.assertEqual(approval_access_list[0]['user_id'], user.id)
        self.assertEqual(approval_access_list[0]['approval_limit']['amount'], first_approval_limit_object['amount'])
        self.assertEqual(approval_access_list[0]['approval_limit']['level'], first_approval_limit_object['level'])
