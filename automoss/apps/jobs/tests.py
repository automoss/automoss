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
from automoss.apps.moss.moss import (
    MOSS,
    RecoverableMossException,
    FatalMossException,
    EmptyResponse
)

User = get_user_model()


class TestJobs(AuthenticatedUserTest):
    """ Test case to test job views """

    def setUp(self):
        super().setUp()

    def _run_test(self, files, expected_status=200):
        job_params = {
            "job-language": "Python",
            "job-max-until-ignored": "10",
            "job-max-displayed-matches": "250",
            'job-name': 'Job Name',
            "files": files
        }
        submit_response = self.client.post(reverse("jobs:new"), job_params)

        response = submit_response.json()
        self.assertEqual(submit_response.status_code, expected_status)

        job_id = response.get('job_id')

        if not job_id:
            return

        process_job(job_id)

        self.assertTrue(isinstance(submit_response, HttpResponse))

        first_match = Match.objects.all().first()

        if first_match:
            report_response = self.client.get(
                reverse("jobs:results:match", kwargs={
                    "job_id": job_id,
                    'match_id': first_match.match_id
                }
                )
            )
            self.assertEqual(report_response.status_code, expected_status)

        Job.objects.get(job_id=job_id).delete()

    def _run_zip_test(self, zip_file):

        archive = zipfile.ZipFile(zip_file, 'r')

        files = []
        for name in archive.namelist():
            files.append(archive.open(name))

        self._run_test(files)

        for file in files:
            file.close()

        archive.close()

    @staticmethod
    def _get_test_files():
        # Submit job
        test_path = os.path.join(TESTS_ROOT, 'test_files', 'zips')

        # Process each zip in test_files
        # TODO improve structure of test files
        for f_name in os.listdir(test_path):
            if os.path.splitext(f_name)[1] == '.zip':
                yield os.path.join(test_path, f_name)

    def test_process_job(self):

        for test_path in self._get_test_files():
            self._run_zip_test(test_path)


    def test_no_files(self):
        self._run_test([], expected_status=400)

    def test_moss_down(self):

        original = MOSS.generate_url

        test_file = next(self._get_test_files())

        errors_to_throw = [
            EmptyResponse,  # MOSS Timed out
            RecoverableMossException,  # Can recover
            FatalMossException,  # Cannot recover
            Exception  # Other error
        ]

        for error_to_throw in errors_to_throw:

            # Override generate_url method to simulate an error being thrown
            def test_method(**kwargs):
                # Set back to original method
                setattr(MOSS, 'generate_url', original)
                raise error_to_throw('Test')

            setattr(MOSS, 'generate_url', test_method)

            self._run_zip_test(test_file)


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
