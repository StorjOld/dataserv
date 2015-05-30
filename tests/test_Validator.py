import unittest
from dataserv.Validator import is_sha256, is_btc_address


class ValidatorTest(unittest.TestCase):
    def test_valid_address(self):
        addr1 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        addr2 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc9999ghjfghj99'
        addr3 = 'not valid address'
        addr4 = 'not valid &address'
        addr5 = '791GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'

        self.assertTrue(is_btc_address(addr1))
        self.assertFalse(is_btc_address(addr2))
        self.assertFalse(is_btc_address(addr3))
        self.assertFalse(is_btc_address(addr4))
        self.assertFalse(is_btc_address(addr5))

    def test_valid_sha256(self):
        valid_hash = '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08'
        self.assertTrue(is_sha256(valid_hash))

        invalid_hash = 'notarealhash'
        self.assertFalse(is_sha256(invalid_hash))
