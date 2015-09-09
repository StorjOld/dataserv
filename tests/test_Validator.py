import unittest
from dataserv.Validator import is_sha256


class ValidatorTest(unittest.TestCase):

    def test_valid_sha256(self):
        ha = '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08'
        self.assertTrue(is_sha256(ha))

        invalid_hash = 'notarealhash'
        self.assertFalse(is_sha256(invalid_hash))
