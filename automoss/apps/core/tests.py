from unittest import TestCase

from .moss import MossResult


class TestMossAPI(TestCase):
    def test_generate(self):
        pass
        # TODO

    def test_parse(self):
        # TODO - store files locally
        test_url = 'http://moss.stanford.edu/results/4/7243339897567/'
        result = MossResult(test_url)

        self.assertEqual(len(result.matches), 3)
