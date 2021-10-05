from ..users.tests import AuthenticatedUserTest
from ...settings import (
    COMPLETED_STATUS,
    TESTS_ROOT
)
from .tasks import process_job
from .models import Job
from ..results.models import Match
from django.utils.timezone import now
from django.http.response import HttpResponse
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import os
import zipfile

User = get_user_model()


class TestJobs(AuthenticatedUserTest):
    """ Test case to test job views """

    def setUp(self):
        super().setUp()

    def test_process_job(self):
        # Submit job
        test_path = os.path.join(TESTS_ROOT, 'test_files', 'zips')

        # Process each zip in test_files
        # TODO improve structure of test files
        for z in os.listdir(test_path):
            if os.path.splitext(z)[1] != '.zip':
                continue  # Ignore non-zip files

            archive = zipfile.ZipFile(os.path.join(test_path, z), 'r')

            files = []
            for name in archive.namelist():
                files.append(archive.open(name))

            job_params = {
                "job-language": "Python",
                "job-max-until-ignored": "10",
                "job-max-displayed-matches": "250",
                'job-name': 'Job Name',
                "files": files
            }
            submit_response = self.client.post(reverse("jobs:new"), job_params)

            response = submit_response.json()
            job_id = response['job_id']
            process_job(job_id)

            for file in files:
                file.close()

            self.assertEqual(submit_response.status_code, 200)
            self.assertTrue(isinstance(submit_response, HttpResponse))
            archive.close()

            first_match = Match.objects.all().first()

            report_response = self.client.get(
                reverse("jobs:results:match", kwargs={
                    "job_id": job_id,
                    'match_id': first_match.match_id
                }
                )
            )
            self.assertEqual(report_response.status_code, 200)

            # Delete job
            Job.objects.get(job_id=job_id).delete()


class TestAPI(AuthenticatedUserTest):
    """ Test case to test user views """

    def setUp(self):
        super().setUp()
        self.test_job = Job.objects.create(user=self.user, status=COMPLETED_STATUS,
                                           start_date=now(), completion_date=now())

    def test_get_jobs(self):
        response = self.client.get(reverse("api:jobs:get_jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, HttpResponse))

    def test_get_statuses(self):
        response = self.client.get(reverse("api:jobs:get_statuses"), {
            'job_ids': self.test_job.job_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, HttpResponse))

    def test_get_logs(self):
        response = self.client.get(reverse("api:jobs:get_logs"), {
            'job_ids': self.test_job.job_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response, HttpResponse))


class TestResults(AuthenticatedUserTest):
    """ Test case to test user views """

    def setUp(self):
        super().setUp()
        self.test_job = Job.objects.create(user=self.user, status=COMPLETED_STATUS,
                                           start_date=now(), completion_date=now())

    def test_get_result(self):
        """ Test successful login attempt """

        report_response = self.client.get(
            reverse("jobs:results:index", kwargs={"job_id": self.test_job.job_id}))
        self.assertEqual(report_response.status_code, 200)
        self.assertTrue(isinstance(report_response, HttpResponse))
