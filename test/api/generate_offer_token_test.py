import copy
from contextlib import nested
from datetime import datetime, timedelta
from mock import patch, MagicMock

# general
from general.exception.errors import deserialize_json
from general.mock.general.util.data_service_property_helper_mock import DataServicePropertyHelperMock
from general.mock.general.util.ls_api.client_api import get_client_mock
from general.mock.general.util.os_api.application_api import get_application
from general.mock.general.util.user_service_property_helper_mock import UserServicePropertyHelperMock

from userservice.app import api
from userservice.app import db as user_service_db
from userservice.app.factories.factories import NotificationTokenFactory
from userservice.app.models import NotificationToken
from userservice.default_config import basedir as userservice_basedir
from general.util.test_helper import BaseTest, TestHttpRequest


class RegenerateOfferTokenTest(BaseTest):

    application_id = 12
    end_point_data = {
        'application_id': application_id,
        'iso_name': "Dummy Iso", 'iso_email': 'test@lendingfront.com',
        'contact_email': 'test@lendingfront.com,',
        'business_id': 77, 'application_source': 'LENDINGPORTAL',
        'user_token': 'eyJhbGciOiJIUYXVsdCIsInVzZXw46Gt9Cth7okXsjoo',
        'client_id': 1, 'business_name': 'Dummy Business Test',
        'notification_token_type': "OFFER_TOKEN", 'contact_name': "Dummy Name"
    }
    __endpoint_url = "/userservice/api/v1.0/user/offer/token"

    @classmethod
    def setUpClass(cls):
        # So the exception would be catch by flask-restful
        api.app.config['PROPAGATE_EXCEPTIONS'] = False
        cls.app = api.app.test_client()

        cls.http_request = TestHttpRequest(cls.app, cls.__endpoint_url)

    def setUp(self):

        application_databases = {
            'userservice': {
                'base_directory': userservice_basedir,
                'db_instance': user_service_db
            }
        }

        self.set_up_db(application_databases, False)

    def get_patches(self):

        patches = {
            'userservice.app.controllers.notification_token.UserServicePropertyHelper': {
                'return_value': UserServicePropertyHelperMock()
            },
            'userservice.app.controllers.notification_token.get_client': {
                'return_value': get_client_mock()
            },
            'userservice.app.controllers.notification_token.get_stipulations': {
                'return_value': {
                    'stipulation_list': [],
                    'active_stipulation_list': [],
                    'lender_stipulation_list': [],
                    'stipulation_form_list': [],
                    'active_stipulation_form_list': [],
                    'active_stipulation_id_list': []
                }
            },
            'userservice.app.controllers.notification_token.get_custom_stipulations': {
                'return_value': {
                    'custom_stipulation_list': [],
                    'active_custom_stipulation_list': []
                }
            },
            'userservice.app.controllers.notification_token.get_application_by_application_id': {
                'return_value': get_application()
            },
            'userservice.app.controllers.notification_token.get_offer_comments': {
                'return_value': {'comments': []}
            },
            'userservice.app.controllers.notification_token.send_offer_token_notification': {
                'return_value': None
            },
            'userservice.app.controllers.notification_token.DocumentController.get_stipulation_no_documents_list': {
                'return_value': []
            },
            'userservice.app.controllers.notification_token.DataServicePropertyHelper': {
                'return_value': DataServicePropertyHelperMock()
            }
        }

        return patches

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_create_new_offer_token_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Verify a new offer token is created when there is not existing token for the given application
        """

        with nested(*self.build_patches(self.get_patches())):

            response = self.http_request.post(self.end_point_data)

            notification_token = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == self.application_id).first()

            self.assertIsNotNone(notification_token)
            self.__verify_success_response(response)

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_refresh_existing_active_offer_token_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Verify a existing active token expiration date is extended instead of creating a new token
        """

        current_date_time = datetime.now()

        token = 'sd7s7d7d8dd9ghnbjaia9'

        NotificationTokenFactory.create(
            application_id=self.application_id, notification_token_type=self.end_point_data['notification_token_type']
            , expiration_date=current_date_time, notification_token_status = 'ACTIVE', token=token, source='')

        with nested(*self.build_patches(self.get_patches())):

            response = self.http_request.post(self.end_point_data)

            notification_tokens = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == self.application_id).all()

            self.assertEqual(1, len(notification_tokens))
            self.assertEqual(9, (notification_tokens[0].expiration_date - datetime.now()).seconds / 3600)
            self.assertEqual(token, notification_tokens[0].token)

            self.__verify_success_response(response)

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_refresh_existing_inactive_offer_token_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Verify a existing inactive token expiration date is extended and status set to active instead of creating a
        new token
        """

        current_date_time = datetime.now()

        token = 'sd7s7d7d8dd9ghnbjaia9'

        NotificationTokenFactory.create(
            application_id=self.application_id, notification_token_type=self.end_point_data['notification_token_type']
            , expiration_date=current_date_time, notification_token_status ='INACTIVE', token=token, source='')

        with nested(*self.build_patches(self.get_patches())):

            response = self.http_request.post(self.end_point_data)

            notification_tokens = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == self.application_id).all()

            self.assertEqual(1, len(notification_tokens))
            self.assertEqual(9, (notification_tokens[0].expiration_date - datetime.now()).seconds / 3600)
            self.assertEqual(token, notification_tokens[0].token)
            self.__verify_success_response(response)

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_two_existing_active_offer_tokens_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Retrieves token that its expiration_date is more recent and is active, instead of retrieving the oldest one
        """

        current_date_time = datetime.now()

        latest_expiration_date_token = 'asd7as7d7asda8sd8a8sd8asd'

        NotificationTokenFactory.create(
            application_id=self.application_id, notification_token_type=self.end_point_data['notification_token_type']
            , expiration_date=current_date_time - timedelta(weeks=1), notification_token_status='ACTIVE',
            token = latest_expiration_date_token, create_date=datetime.now() - timedelta(hours=1), source='')

        NotificationTokenFactory.create(
            application_id=self.application_id, notification_token_type=self.end_point_data['notification_token_type']
            , expiration_date=current_date_time - timedelta(weeks=2), notification_token_status='ACTIVE',
            create_date=datetime.now(), source='')

        with nested(*self.build_patches(self.get_patches())):

            response = self.http_request.post(self.end_point_data)

            response_data = self.__verify_success_response(response)
            self.assertTrue('token' in response_data)
            self.assertEquals(str(latest_expiration_date_token), response_data['token'])

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_create_another_not_offer_token_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Verify a second non offer token (Ie, bank enrollment token) is created when there is a existing token for
        the given application,
        """

        end_point_data = copy.deepcopy(self.end_point_data)
        end_point_data['notification_token_type'] = "BANK_ENROLLMENT_TOKEN"

        NotificationTokenFactory.create(
            application_id=self.application_id, notification_token_type=end_point_data['notification_token_type'],
            expiration_date=datetime.now(), source='')

        with nested(*self.build_patches(self.get_patches())):

            response = self.http_request.post(end_point_data)

            inactive_notification_token = user_service_db.session.query(NotificationToken).filter_by(
                application_id=self.application_id, notification_token_status='INACTIVE').first()

            self.assertIsNotNone(inactive_notification_token)

            active_notification_token = user_service_db.session.query(NotificationToken).filter_by(
                application_id=self.application_id, notification_token_status='ACTIVE').first()

            self.assertIsNotNone(active_notification_token)
            self.assertNotEqual(active_notification_token.id, inactive_notification_token.id)
            self.assertEqual(10, (active_notification_token.expiration_date - inactive_notification_token.expiration_date).seconds / 3600)

            self.__verify_success_response(response)

    @patch('flask_jwt.verify_jwt', return_value=False)
    @patch('flask_jwt._request_ctx_stack')
    def test_create_new_not_offer_token_success(self, mock_request_ctx_stack, jwt_required_fn):
        """
        Verify a new non offer token (ie bank enrollment token) is created when there is not existing token for
        the given application
        """

        end_point_data = copy.deepcopy(self.end_point_data)
        end_point_data['notification_token_type'] = "BANK_ENROLLMENT_TOKEN"

        with nested(*self.build_patches(self.get_patches())):

            response = self.http_request.post(end_point_data)

            notification_token = user_service_db.session.query(NotificationToken).filter(
                NotificationToken.application_id == self.application_id).first()

            self.assertIsNotNone(notification_token)
            self.__verify_success_response(response)

    def __verify_success_response(self, response):
        response_data = deserialize_json(response.data)
        self.assertTrue('status' in response_data)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual("OK", response_data['status'])
        self.assertEqual("Notification token successfully created", response_data['message'])
        return response_data
