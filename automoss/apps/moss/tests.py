from ..users.tests import AuthenticatedUserTest
from django.urls import reverse
from .pinger import Pinger
from unittest import TestCase
import os
from .moss import (
    MOSS,
    is_valid_moss_url,
    InvalidReportURL,
    ReportParsingError
)
from ...settings import DEFAULT_MOSS_SETTINGS, TESTS_ROOT


class TestMossAPI(TestCase):
    """Class which controls test cases for the MOSS API"""

    def test_upload_and_parse(self):
        """Upload a job to MOSS and parse the result"""

        base_dir = os.path.join(TESTS_ROOT, 'test_files')

        paths = {
            'files': [],
            'base_files': []
        }
        for file_type in paths:
            path = os.path.join(base_dir, file_type)
            if os.path.isdir(path):
                paths[file_type] = [os.path.join(path, k)
                                    for k in os.listdir(path)]

        if not paths['files']:
            return

        moss_user_id = 1  # TODO use environment variables
        result = MOSS.generate(
            user_id=moss_user_id,
            language='python',
            **paths,
            max_until_ignored=DEFAULT_MOSS_SETTINGS['max_until_ignored'],
            max_displayed_matches=DEFAULT_MOSS_SETTINGS['max_displayed_matches'],
            comment='',
            use_basename=True
        )

        self.assertTrue(is_valid_moss_url(result.url))

    def test_invalid(self):
        """Test invalid moss results"""

        with self.assertRaises(InvalidReportURL):
            MOSS.generate_report('invalid_url')

        with self.assertRaises(ReportParsingError):
            MOSS.generate_report(
                'http://moss.stanford.edu/results/0/1234567890')


class TestJobs(AuthenticatedUserTest):
    """ Test case to test job views """

    def setUp(self):
        super().setUp()

    def test_ping_moss(self):
        """Test pinging MOSS"""
        Pinger.ping()
        response = self.client.get(reverse("api:moss:get_status"))
        self.assertEqual(response.status_code, 200)
