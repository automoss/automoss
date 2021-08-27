from unittest import TestCase
import os
from .moss import (
    MossResult,
    MOSS,
    is_valid_moss_url
)
from ...defaults import (
    MAX_UNTIL_IGNORED,
    MAX_DISPLAYED_MATCHES
)


class TestMossAPI(TestCase):
    def test_upload_and_parse(self):

        base_dir = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'test')
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
        result = MOSS(moss_user_id).generate(
            language='python',
            **paths,
            max_matches_until_ignore=MAX_UNTIL_IGNORED,
            num_to_show=MAX_DISPLAYED_MATCHES,
            comment='',
            use_basename=True
        )

        self.assertTrue(is_valid_moss_url(result.url))
