import json
from contextlib import nested

from datetime import datetime
from mock import patch, MagicMock

# general
from general.auth.user import User
from general.exception.errors import deserialize_json
from general.mock.general.util.data_service_property_helper_mock import DataServicePropertyHelperMock
from general.mock.general.util.loan_service_property_helper_mock import LoanServicePropertyHelperMock
from general.mock.general.util.lending_portal_property_helper_mock import LendingPortalPropertyHelperMock
from general.mock.general.util.ls_api.client_api import get_client_mock
from general.mock.general.util.os_api.application_api import get_application
from general.mock.general.util.user_service_property_helper_mock import UserServicePropertyHelperMock
from general.util.test_helper import TestMockMixin, TestInMemoryDatabaseMixin, BaseTest
from general.test.data.user_data import get_user_data

from userservice.app import api
from userservice.app import db as user_service_db
from userservice.app.factories.factories import NotificationTokenFactory
from userservice.app.models import NotificationToken
from userservice.default_config import basedir as userservice_basedir


class GetTokenTest(BaseTest):

    client_id = 1
    endpoint_url = "/userservice/api/v1.0/user/notification/token"
    user_test = get_user_data(client_id)

    def get_patches(self, new_patches=None):
        """
        Builds the mock patches
        :param new_patches: Dict
        :return: Patches dict
        """
        patches = {
            'userservice.app.user.UserServicePropertyHelper': {
                'return_value': UserServicePropertyHelperMock()
            },
            'userservice.app.user.LoanServicePropertyHelper': {
                'return_value': LoanServicePropertyHelperMock()
            },
            'userservice.app.user.get_client': {
                'return_value': get_client_mock()
            },
            'userservice.app.user.generated_token_notification': {
                'return_value': None
            },
            'userservice.app.user.generated_notification_token_notification': {
                'return_value': None
            },
            'userservice.app.user.application_api.get_application_by_application_id': {
                'return_value': get_application()
            },
            'userservice.app.user.application_api.get_offer_comments': {
                'return_value': { 'comments': [] }
            },
            'userservice.app.user.LendingPortalPropertyHelper': {
                'return_value': LendingPortalPropertyHelperMock()
            },
            'userservice.app.controllers.notification_token.DataServicePropertyHelper': {
                'return_value': DataServicePropertyHelperMock()
            }
        }

        if new_patches is not None:
            for key, value in new_patches.iteritems():
                patches[key] = value

        return self.build_patches(patch_dict=patches)

    def setUp(self):
        application_databases = {
            'userservice': {
                'base_directory': userservice_basedir,
                'db_instance': user_service_db
            }
        }
        self.set_up_db(application_databases, create_files=False)
        api.app.config['PROPAGATE_EXCEPTIONS'] = False
        self.app = api.app.test_client()

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def generate_plaid_token_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test generate a  token with plaid source
        """

        with nested(*self.get_patches()):

            mock_request_ctx_stack.top.current_user = User(self.user_test)

            end_point_data = {'iso_contact': None,
                              'first_name': 'Dummy Test', 'application_id': 1, 'lender_stipulations': None,
                              'iso_name': None, 'final_path': None, 'email': 'test@lendingfront.com,',
                              'business_id': 77, 'file_path': None, 'application_source': 'LENDINGPORTAL',
                              'user_token': 'eyJhbGciOiJIUYXVsdCIsInVzZXw46Gt9Cth7okXsjoo',
                              'stipulations': None, 'client_id': 1, 'iso_email': None, 'business_name': 'Dummy Test',
                              'notification_token_type': 'BANK_ENROLLMENT_TOKEN', 'last_name': 'Dummy Test'}

            self.app.post(self.endpoint_url,
                          data=json.dumps(end_point_data),
                          content_type='application/json')

            notification_token = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == 1).first()

            self.assertEqual("PLAID", notification_token.source)

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def generate_yodlee_token_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test generate a token with yodlee source
        """

        data_service_property_helper_mock = DataServicePropertyHelperMock()
        data_service_property_helper_mock.get_client_cashflow_source = MagicMock(
            return_value="YODLEE")

        patch_dic = {'userservice.app.controllers.notification_token.DataServicePropertyHelper':
                         {'return_value': data_service_property_helper_mock}}

        with nested(*self.get_patches(patch_dic)):
            mock_request_ctx_stack.top.current_user = User(self.user_test)

            end_point_data = {'iso_contact': None,
                              'first_name': 'Dummy Test', 'application_id': 2, 'lender_stipulations': None,
                              'iso_name': None, 'final_path': None, 'email': 'test@lendingfront.com,',
                              'business_id': 77, 'file_path': None, 'application_source': 'LENDINGPORTAL',
                              'user_token': 'eyJhbGciOiJIUYXVsdCIsInVzZXw46Gt9Cth7okXsjoo',
                              'stipulations': None, 'client_id': 1, 'iso_email': None, 'business_name': 'Dummy Test',
                              'notification_token_type': 'BANK_ENROLLMENT_TOKEN', 'last_name': 'Dummy Test'}

            self.app.post(self.endpoint_url,
                          data=json.dumps(end_point_data),
                          content_type='application/json')

            notification_token = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == 2).first()

            self.assertEqual("YODLEE", notification_token.source)

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def generate_non_source_token_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test generate a token without source
        """

        data_service_property_helper_mock = DataServicePropertyHelperMock()
        data_service_property_helper_mock.get_client_cashflow_source = MagicMock(
            return_value="YODLEE")

        patch_dic = {'userservice.app.controllers.notification_token.DataServicePropertyHelper':
                         {'return_value': data_service_property_helper_mock}}

        with nested(*self.get_patches(patch_dic)):
            mock_request_ctx_stack.top.current_user = User(self.user_test)

            end_point_data = {'iso_contact': None,
                              'first_name': 'Dummy Test', 'application_id': 3, 'lender_stipulations': None,
                              'iso_name': None, 'final_path': None, 'email': 'test@lendingfront.com,',
                              'business_id': 77, 'file_path': None, 'application_source': 'LENDINGPORTAL',
                              'user_token': 'eyJhbGciOiJIUYXVsdCIsInVzZXw46Gt9Cth7okXsjoo',
                              'stipulations': None, 'client_id': 1, 'iso_email': None, 'business_name': 'Dummy Test',
                              'notification_token_type': 'E_SIGN_TOKEN', 'last_name': 'Dummy Test'}

            self.app.post(self.endpoint_url,
                          data=json.dumps(end_point_data),
                          content_type='application/json')

            notification_token = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == 3).first()

            self.assertEqual("", notification_token.source)

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def get_yodlee_notification_token_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test get token with yodlee source
        """

        with nested(*self.get_patches()):

            mock_request_ctx_stack.top.current_user = User(self.user_test)
            NotificationTokenFactory.create(source="YODLEE")

            end_point_data = {'application_id': 1,
                              'notification_token_type': 'BANK_ENROLLMENT_TOKEN', 'last_name': 'Dummy Test'}

            response = self.app.get(self.endpoint_url,
                                    data=json.dumps(end_point_data),
                                    content_type='application/json')

            response_data = deserialize_json(response.data)

            self.assertTrue('status' in response_data)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual("OK", response_data['status'])
            self.assertEqual(response_data['source'], "YODLEE")

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def get_plaid_notification_token_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test get a token without  plaid source
        """

        with nested(*self.get_patches()):

            NotificationTokenFactory.create()

            end_point_data = {'iso_contact': None,
                              'first_name': 'Dummy Test', 'application_id': 1, 'lender_stipulations': None,
                              'iso_name': None, 'final_path': None, 'email': 'test@lendingfront.com,',
                              'business_id': 77, 'file_path': None, 'application_source': 'LENDINGPORTAL',
                              'user_token': 'eyJhbGciOiJIUYXVsdCIsInVzZXw46Gt9Cth7okXsjoo',
                              'stipulations': None, 'client_id': 1, 'iso_email': None, 'business_name': 'Dummy Test',
                              'notification_token_type': 'BANK_ENROLLMENT_TOKEN', 'last_name': 'Dummy Test'}

            response = self.app.get(self.endpoint_url,
                                    data=json.dumps(end_point_data),
                                    content_type='application/json')

            response_data = deserialize_json(response.data)

            self.assertTrue('status' in response_data)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual("OK", response_data['status'])
            self.assertEqual(response_data['source'], "PLAID")

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def get_plaid_notification_token_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test get a token without  plaid source
        """
        with nested(*self.get_patches()):
            NotificationTokenFactory.create()

            end_point_data = {'iso_contact': None,
                              'first_name': 'Dummy Test', 'application_id': 1, 'lender_stipulations': None,
                              'iso_name': None, 'final_path': None, 'email': 'test@lendingfront.com,',
                              'business_id': 77, 'file_path': None, 'application_source': 'LENDINGPORTAL',
                              'user_token': 'eyJhbGciOiJIUYXVsdCIsInVzZXw46Gt9Cth7okXsjoo',
                              'stipulations': None, 'client_id': 1, 'iso_email': None, 'business_name': 'Dummy Test',
                              'notification_token_type': 'BANK_ENROLLMENT_TOKEN', 'last_name': 'Dummy Test'}

            response = self.app.get(self.endpoint_url,
                                    data=json.dumps(end_point_data),
                                    content_type='application/json')

            response_data = deserialize_json(response.data)

            self.assertTrue('status' in response_data)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual("OK", response_data['status'])
            self.assertEqual(response_data['source'], "PLAID")

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def generate_plaid_bank_enrollment_update_notification_token_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test /userservice/api/v1.0/user/notification/bankenrollment/update/token with plaid source
        """

        with nested(*self.get_patches()):
            endpoint_url = "/userservice/api/v1.0/user/notification/bankenrollment/update/token"
            application_id = 10

            end_point_data = {'application_id': application_id, 'email': 'test@lendingfront.com,',
                              'business_id': 77, 'client_id': 1, 'notification_token_type': 'BANK_ENROLLMENT_TOKEN'}

            response = self.app.post(endpoint_url,
                                     data=json.dumps(end_point_data),
                                     content_type='application/json')

            response_data = deserialize_json(response.data)

            notification_token = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == application_id).first()

            self.assertTrue('status' in response_data)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual("OK", response_data['status'])
            self.assertEqual("Notification token successfully created", response_data['message'])
            self.assertEqual("PLAID", notification_token.source)

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def generate_yodlee_bank_enrollment_update_notification_token_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test /userservice/api/v1.0/user/notification/bankenrollment/update/token with  yodlee source
        """

        data_service_property_helper_mock = DataServicePropertyHelperMock()
        data_service_property_helper_mock.get_client_cashflow_source = MagicMock(
            return_value="YODLEE")

        patch_dic = {'userservice.app.controllers.notification_token.DataServicePropertyHelper':
                         {'return_value': data_service_property_helper_mock}}

        with nested(*self.get_patches(patch_dic)):

            endpoint_url = "/userservice/api/v1.0/user/notification/bankenrollment/update/token"
            application_id = 11

            end_point_data = {'application_id': application_id, 'email': 'test@lendingfront.com,',
                              'business_id': 77, 'client_id': 1, 'notification_token_type': 'BANK_ENROLLMENT_TOKEN'}

            response = self.app.post(endpoint_url,
                                     data=json.dumps(end_point_data),
                                     content_type='application/json')

            response_data = deserialize_json(response.data)

            notification_token = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == application_id).first()

            self.assertTrue('status' in response_data)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual("OK", response_data['status'])
            self.assertEqual("Notification token successfully created", response_data['message'])
            self.assertEqual("YODLEE", notification_token.source)

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def generate_plaid_bank_enrollment_update_notification_token_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test /userservice/api/v1.0/user/notification/bankenrollment/update/token with plaid source
        """

        with nested(*self.get_patches()):

            endpoint_url = "/userservice/api/v1.0/user/notification/bankenrollment/update/token"
            application_id = 10

            end_point_data = {'application_id': application_id, 'email': 'test@lendingfront.com,',
                              'business_id': 77, 'client_id': 1, 'notification_token_type': 'BANK_ENROLLMENT_TOKEN'}

            response = self.app.post(endpoint_url,
                                     data=json.dumps(end_point_data),
                                     content_type='application/json')

            response_data = deserialize_json(response.data)

            notification_token = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == application_id).first()

            self.assertTrue('status' in response_data)
            self.assertEqual(response.status, '200 OK')
            self.assertEqual("OK", response_data['status'])
            self.assertEqual("Notification token successfully created", response_data['message'])
            self.assertEqual("PLAID", notification_token.source)

    @patch('general.util.jwt_helper.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def update_existing_notification_token_expiration_test(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Test the expiration date update for a existing notification token
        """

        with nested(*self.get_patches()):

            mock_request_ctx_stack.top.current_user = User(self.user_test)

            expiration_date = datetime.now()

            token_data = {'email': 'test@lendingfront.com,', 'create_date': datetime(year=2018, month=1, day=2),
                          'expiration_date': expiration_date,
                          'token': 'eyJhbGciOiJIUYXVsdCIsInVzZXw46Gt9Cth7okXsjoo',
                          'notification_token_type': 'E_SIGN_TOKEN', 'notification_token_status': "ACTIVE",
                          'business_id': 77, 'application_id': 1, 'source': '',
                          'client_id': 1}
            NotificationTokenFactory.create(**token_data)

            end_point_data = {'iso_contact': None,
                              'first_name': 'Dummy Test', 'application_id': 1, 'lender_stipulations': None,
                              'iso_name': None, 'final_path': None, 'email': 'test@lendingfront.com,',
                              'business_id': 77, 'file_path': None, 'application_source': 'LENDINGPORTAL',
                              'user_token': 'eyJhbGciOiJIUYXVsdCIsInVzZXw46Gt9Cth7okXsjoo',
                              'stipulations': None, 'client_id': 1, 'iso_email': None, 'business_name': 'Dummy Test',
                              'notification_token_type': 'E_SIGN_TOKEN', 'last_name': 'Dummy Test'}

            self.app.post(self.endpoint_url,
                          data=json.dumps(end_point_data),
                          content_type='application/json')

            notification_token = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == 1).first()

            self.assertGreater(notification_token.expiration_date, expiration_date)
