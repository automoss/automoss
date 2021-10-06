from django.http.response import HttpResponse
from django.test import TestCase
from django.test import Client
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from .tokens import confirm_registration_token

User = get_user_model()


class AuthenticatedUserTest(TestCase):
    """ Base class for test cases, creating an authenticated client for testing """

    def setUp(self):
        """ Test case setup """
        # User Creation
        self.credentials = {
            'course_code': 'user',
            'primary_email_address': 'test@localhost',
            'moss_id': 1,
            'password': 'Testing123!',
            'is_verified': True
        }
        self.login_credentials = {
            'username': self.credentials['course_code'],
            'password': self.credentials['password']
        }

        self.user = User.objects.create_user(**self.credentials)

        # Create client and log them in
        self.client, _ = self.create_client()

    def create_client(self, login_credentials=None):
        # if login_credentials is None, use default

        client = Client()

        login_response = client.post(
            reverse("users:login"), login_credentials or self.login_credentials)

        return client, login_response


class TestUsers(AuthenticatedUserTest):

    def test_user_creation(self):
        """ Test user creation """
        self.assertEqual(self.user.course_code,
                         self.credentials.get('course_code'))
        self.assertEqual(self.user.primary_email_address,
                         self.credentials.get('primary_email_address'))
        self.assertEqual(self.user.moss_id,
                         self.credentials.get('moss_id'))
        self.assertEqual(self.user.is_verified,
                         self.credentials.get('is_verified'))
        self.assertNotEqual(self.user.password,
                            self.credentials.get('password'))

    def test_staff_user_creation(self):
        User.objects.create_staffuser(
            course_code='staff',
            primary_email_address='staff@localhost',
            moss_id=2,
            password='Testing123!',
            is_verified=True
        )

    def test_super_user_creation(self):
        User.objects.create_superuser(
            course_code='super',
            primary_email_address='super@localhost',
            moss_id=3,
            password='Testing123!',
            is_verified=True
        )

    def test_login_success(self):
        """ Test successful login attempt """
        test_client, login_response = self.create_client()

        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(isinstance(login_response, HttpResponseRedirect))
        self.assertEqual(login_response.get("Location"), reverse("jobs:index"))
        self.assertIn('_auth_user_id', test_client.session)

    def test_login_fail(self):
        """ Test failed login attempt """
        test_client, login_response = self.create_client(
            {"username": "1", "password": "1"})
        # Failed Login

        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(isinstance(login_response, HttpResponse)
                        and not isinstance(login_response, HttpResponseRedirect))
        self.assertNotIn('_auth_user_id', test_client.session)

    def test_logout(self):
        """ Test logout """

        # Login
        test_client, login_response = self.create_client()

        self.assertIn('_auth_user_id', test_client.session)
        # Logout
        logout_response = test_client.get(reverse("users:logout"))
        self.assertEqual(logout_response.status_code, 200)
        self.assertTrue(isinstance(logout_response, HttpResponse)
                        and not isinstance(logout_response, HttpResponseRedirect))
        self.assertNotIn('_auth_user_id', test_client.session)

    def test_login_page_unauth(self):
        """ Test get login page when unauthenticated """
        test_client = Client()
        # Get login page
        login_response = test_client.get(reverse("users:login"))
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(isinstance(login_response, HttpResponse))

    def test_login_page_auth(self):
        """ Test get login page when authenticated """

        test_client, login_response = self.create_client()

        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(isinstance(login_response, HttpResponseRedirect))
        self.assertEqual(login_response.get("Location"), reverse("jobs:index"))

    def test_register_and_confirm(self):
        cases = [
            ({
                'course_code': 'CSC3003S',
                'primary_email_address': 'testing@testingautomoss.com',
                'moss_id': '2',
                'password1': 'Testing123!',
                'password2': 'Testing123!'
            }, True),  # Normal Details
            ({
                'course_code': 'jdkf8923fUd0f023iflkdsdf13rar',
                'primary_email_address': '0djf302f23df23r2@asdf2345asdfglkvaa34atvwerjt.com',
                'moss_id': '3',
                'password1': '1249uvnw89erhg89gh3r!@#%(465v0236 35 qw4trv239JDWIW',
                'password2': '1249uvnw89erhg89gh3r!@#%(465v0236 35 qw4trv239JDWIW'
            }, True),  # Normal Details
            ({
                'course_code': 'test_user',
                'primary_email_address': 'testing@test.com',
                'moss_id': '2',
                'password1': 'Testing123!',
                'password2': 'Testing123!'
            }, False),  # Course Code already exists
            ({
                'course_code': 'CSC3002F',
                'primary_email_address': 'testing@test',
                'moss_id': '2',
                'password1': 'Testing123!',
                'password2': 'Testing123!'
            }, False),  # Invalid Email
            ({
                'course_code': 'CSC3002F',
                'primary_email_address': 'testing@test.com',
                'moss_id': '0',
                'password1': 'Testing123!',
                'password2': 'Testing123!'
            }, False),  # Invalid MOSS ID
            ({
                'course_code': 'CSC3002F',
                'primary_email_address': 'testing@test.com',
                'moss_id': '1',
                'password1': 'Testing123!',
                'password2': 'Testing123!'
            }, False),  # MOSS ID already exists
            ({
                'course_code': 'CSC3002F',
                'primary_email_address': 'testing@test.com',
                'moss_id': '3',
                'password1': 'Testing123',
                'password2': 'Testing123!'
            }, False),  # Passwords do not match
            ({
                'course_code': 'CSC3002F',
                'primary_email_address': 'testing@test.com',
                'moss_id': '3',
                'password1': 'Testing',
                'password2': 'Testing'
            }, False),  # Passwords not secure
        ]
        # For each case
        for details, outcome in cases:
            test_client = Client()

            # Post registration details
            register_response = test_client.post(
                reverse("users:register"), details)

            # Outcome success should be able to confirm account and authenticate
            if outcome:
                # Find user in database
                user = User.objects.get(course_code=details.get('course_code'))

                # user should not be verified or logged in
                self.assertFalse(user.is_verified)
                self.assertNotIn('_auth_user_id', test_client.session)

                # confirm using verification link
                verify_response = test_client.get(
                    reverse("users:confirm", kwargs={
                        'uid': user.user_id,
                        'token': confirm_registration_token.make_token(user)
                    }
                    )
                )
                # Login to account
                test_client.post(reverse("users:login"), {
                    'username': details.get('course_code'),
                    'password': details.get('password1')
                }
                )
                self.assertEqual(register_response.status_code, 200)
                self.assertEqual(verify_response.status_code, 200)
                self.assertTrue(isinstance(register_response, HttpResponse))
                self.assertTrue(isinstance(verify_response, HttpResponse))

                # Logged in
                self.assertIn('_auth_user_id', test_client.session)

            # Outcome fail should not redirect and should not authenticate
            else:
                self.assertEqual(register_response.status_code, 200)
                self.assertTrue(isinstance(register_response, HttpResponse) and not isinstance(
                    register_response, HttpResponseRedirect))
                self.assertNotIn('_auth_user_id', test_client.session)
                self.assertFalse(user.is_verified)
