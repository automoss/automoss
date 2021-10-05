from unittest import TestCase
import os
from .moss import (
    Result,
    MOSS,
    is_valid_moss_url,
    InvalidReportURL,
    ReportParsingError,
    FatalMossException
)
from ...settings import DEFAULT_MOSS_SETTINGS, TESTS_ROOT


class TestMossAPI(TestCase):
    def test_upload_and_parse(self):

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

        with self.assertRaises(InvalidReportURL) as context:
            invalid_url = MOSS.generate_report('invalid_url')
        
        with self.assertRaises(ReportParsingError) as context:
            invalid_moss_report = MOSS.generate_report('http://moss.stanford.edu/results/0/1234567890')
