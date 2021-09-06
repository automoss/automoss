from django.http.response import HttpResponse
from django.test import TestCase
from django.test import Client
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class TestUsers(TestCase):
    """ Test case to test user views """

    def setUp(self):
        """ Test case setup """
        # User Creation
        self.credentials = {
            'course_code': 'test_user',
            'primary_email_address': 'test@localhost',
            'moss_id': 1,
            'password': 'Testing123!'}
        self.login_credentials = {'username': self.credentials.get('course_code'), 'password': self.credentials.get('password')}
        self.test_user = User.objects.create_user(**self.credentials)

    def test_user_creation(self):
        """ Test user creation """
        self.assertEqual(self.test_user.course_code, self.credentials.get('course_code'))
        self.assertEqual(self.test_user.primary_email_address, self.credentials.get('primary_email_address'))
        self.assertEqual(self.test_user.moss_id, self.credentials.get('moss_id'))
        self.assertNotEqual(self.test_user.password, self.credentials.get('password'))

    def test_login_success(self):
        """ Test successful login attempt """
        test_client = Client()
        # Successful Login
        login_response = test_client.post(reverse("users:login"), self.login_credentials)
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(isinstance(login_response, HttpResponseRedirect))
        self.assertEqual(login_response.get("Location"), reverse("jobs:index"))
        self.assertIn('_auth_user_id', test_client.session)

    def test_login_fail(self):
        """ Test failed login attempt """
        test_client = Client()
        # Failed Login
        login_response = test_client.post(reverse("users:login"), {"username" : "1", "password": "1"})
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(isinstance(login_response, HttpResponse) and not isinstance(login_response, HttpResponseRedirect))
        self.assertNotIn('_auth_user_id', test_client.session)

    def test_logout(self):
        """ Test logout """
        test_client = Client()
        # Login
        test_client.post(reverse("users:login"), self.login_credentials)
        self.assertIn('_auth_user_id', test_client.session)
        # Logout
        logout_response = test_client.get(reverse("users:logout"))
        self.assertEqual(logout_response.status_code, 200)
        self.assertTrue(isinstance(logout_response, HttpResponse) and not isinstance(logout_response, HttpResponseRedirect))
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
        test_client = Client()
        # Login
        test_client.post(reverse("users:login"), self.login_credentials)
        # Get login page
        login_response = test_client.get(reverse("users:login"))
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(isinstance(login_response, HttpResponseRedirect))
        self.assertEqual(login_response.get("Location"), reverse("jobs:index"))

    def test_register(self):
        cases = [
            ({
            'course_code': 'CSC3003S',
            'primary_email_address': 'testing@test.com',
            'moss_id': '2',
            'password1': 'Testing123!',
            'password2': 'Testing123!'
            }, True), # Normal Details
            ({
            'course_code': 'test_user',
            'primary_email_address': 'testing@test.com',
            'moss_id': '2',
            'password1': 'Testing123!',
            'password2': 'Testing123!'
            }, False), # Course Code already exists
            ({
            'course_code': 'CSC3002F',
            'primary_email_address': 'testing@test',
            'moss_id': '2',
            'password1': 'Testing123!',
            'password2': 'Testing123!'
            }, False), # Invalid Email
            ({
            'course_code': 'CSC3002F',
            'primary_email_address': 'testing@test.com',
            'moss_id': '0',
            'password1': 'Testing123!',
            'password2': 'Testing123!'
            }, False), # Invalid MOSS ID
            ({
            'course_code': 'CSC3002F',
            'primary_email_address': 'testing@test.com',
            'moss_id': '1',
            'password1': 'Testing123!',
            'password2': 'Testing123!'
            }, False), # MOSS ID already exists
            ({
            'course_code': 'CSC3002F',
            'primary_email_address': 'testing@test.com',
            'moss_id': '3',
            'password1': 'Testing123',
            'password2': 'Testing123!'
            }, False), # Passwords do not match
            ({
            'course_code': 'CSC3002F',
            'primary_email_address': 'testing@test.com',
            'moss_id': '3',
            'password1': 'Testing',
            'password2': 'Testing'
            }, False), # Passwords not secure
        ]
        # For each case
        for details, outcome in cases:
            test_client = Client()
            # Post registration details
            register_response = test_client.post(reverse("users:register"), details)
            # Outcome success should authenticate and redirect to jobs index
            if outcome:
                self.assertEqual(register_response.status_code, 302)
                self.assertTrue(isinstance(register_response, HttpResponseRedirect))
                self.assertEqual(register_response.get("Location"), reverse("jobs:index"))
                self.assertIn('_auth_user_id', test_client.session)
            # Outcome fail should not redirect and should not authenticate
            else:
                self.assertEqual(register_response.status_code, 200)
                self.assertTrue(isinstance(register_response, HttpResponse) and not isinstance(register_response, HttpResponseRedirect))
                self.assertNotIn('_auth_user_id', test_client.session)