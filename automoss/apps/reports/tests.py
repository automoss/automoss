from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.test import TestCase
from django.test import Client
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from ..users.models import MOSSUser
from .models import MOSSReport
from ..jobs.models import Job
from django.contrib.auth.models import User
from django.urls import reverse
from ...defaults import (
    COMPLETED_STATUS
)

class TestReports(TestCase):
    """ Test case to test user views """

    def setUp(self):
        """ Test case setup """
        # User Creation
        self.credentials = {
            'username': 'test_user',
            'password': 'Testing123!'}
        self.test_user = User.objects.create_user(**self.credentials)
        self.test_moss_user = MOSSUser.objects.create(user=self.test_user, moss_id=1)
        # Job Creation
        self.test_job = Job.objects.create(moss_user=self.test_moss_user, status=COMPLETED_STATUS, 
        start_date=now(), completion_date=now())
        # Report Creation 
        self.test_report = MOSSReport.objects.create(job=self.test_job, url="/")

    def test_get_report(self):
        """ Test successful login attempt """
        test_client = Client()
        # Login
        test_client.post(reverse("users:login"), self.credentials)
        # Get report
        report_response = test_client.get(reverse("jobs:reports:index", kwargs={"job_id": self.test_job.job_id}), self.credentials)
        self.assertEqual(report_response.status_code, 200)
        self.assertTrue(isinstance(report_response, HttpResponse))
