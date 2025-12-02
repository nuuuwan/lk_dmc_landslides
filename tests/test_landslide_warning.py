import unittest

from lk_dmc import LandslideWarning


class TestCase(unittest.TestCase):
    def test_list_from_remote(self):
        lw_list = LandslideWarning.list_from_remote()
        self.assertIsInstance(lw_list, list)
        self.assertGreater(len(lw_list), 0)
