from django.http.response import HttpResponse
from django.test import TestCase
from django.test import Client
from django.http import HttpResponseRedirect
from .models import MOSSUser
from django.contrib.auth.models import User
from django.urls import reverse

class TestUsers(TestCase):
    """ Test case to test user views """

    def setUp(self):
        """ Test case setup """
        # User Creation
        self.credentials = {
            'username': 'test_user',
            'password': 'Testing123!'}
        self.test_user = User.objects.create_user(**self.credentials)
        self.test_moss_user = MOSSUser.objects.create(user=self.test_user, moss_id=1)

    def test_login_success(self):
        """ Test successful login attempt """
        test_client = Client()
        # Successful Login
        login_response = test_client.post(reverse("users:login"), self.credentials)
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(isinstance(login_response, HttpResponseRedirect))
        self.assertEqual(login_response.get("Location"), reverse("jobs:index"))

    def test_login_fail(self):
        """ Test failed login attempt """
        test_client = Client()
        # Failed Login
        login_response = test_client.post(reverse("users:login"), {"username" : "1", "password": "1"})
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(isinstance(login_response, HttpResponse) and not isinstance(login_response, HttpResponseRedirect))

    def test_logout(self):
        """ Test logout """
        test_client = Client()
        # Login
        test_client.post(reverse("users:login"), self.credentials)
        # Logout
        logout_response = test_client.get(reverse("users:logout"))
        self.assertEqual(logout_response.status_code, 200)
        self.assertTrue(isinstance(logout_response, HttpResponse) and not isinstance(logout_response, HttpResponseRedirect))

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
        test_client.post(reverse("users:login"), self.credentials)
        # Get login page
        login_response = test_client.get(reverse("users:login"))
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(isinstance(login_response, HttpResponseRedirect))
        self.assertEqual(login_response.get("Location"), reverse("jobs:index"))