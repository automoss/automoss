from django.http.response import HttpResponse
from django.test import TestCase
from django.test import Client
from ..users.models import MOSSUser
from django.contrib.auth.models import User
from django.urls import reverse
import os

class TestJobs(TestCase):
    """ Test case to test job views """

    def setUp(self):
        """ Test case setup """
        # User creation
        self.credentials = {
            'username': 'test_user',
            'password': 'Testing123!'}
        self.test_user = User.objects.create_user(**self.credentials)
        self.test_moss_user = MOSSUser.objects.create(user=self.test_user, moss_id=1)

    def test_new_job(self):
        """ Test submission of job """
        # TODO Add celery/redis support (just tests view at the moment)
        test_client = Client()
        # Login
        test_client.post(reverse("users:login"), self.credentials)
        # Submit job
        test_files_names = ["automoss/apps/jobs/test_files/ta_defs.py", "automoss/apps/jobs/test_files/ta_common.py", "automoss/apps/jobs/test_files/ta_func.py"]
        files = []
        for file in test_files_names:
            open_file = open(file, "rb")
            files.append(open_file)
        job_params = {"job-language":"Python", "job-max-until-ignored":"10", "job-max-displayed-matches":"250", "files": files}
        submit_response = test_client.post(reverse("jobs:new"), job_params)
        for file in files:
            file.close()
        self.assertEqual(submit_response.status_code, 200)
        self.assertTrue(isinstance(submit_response, HttpResponse))
