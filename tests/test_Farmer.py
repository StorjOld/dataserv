import unittest
from dataserv.Farmer import Farmer


class FarmerTest(unittest.TestCase):
    def test_valid_address(self):
        addr1 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        addr2 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc9999ghjfghj99'
        addr3 = 'not valid address'
        addr4 = 'not valid &address'
        addr5 = '791GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'

        farmer1 = Farmer(addr1)
        farmer2 = Farmer(addr2)
        farmer3 = Farmer(addr3)
        farmer4 = Farmer(addr4)
        farmer5 = Farmer(addr5)

        self.assertTrue(farmer1.is_btc_address())
        self.assertFalse(farmer2.is_btc_address())
        self.assertFalse(farmer3.is_btc_address())
        self.assertFalse(farmer4.is_btc_address())
        self.assertFalse(farmer5.is_btc_address())

    def test_address_error(self):
        addr1 = 'not valid address'
        farmer1 = Farmer(addr1)
        self.assertRaises(ValueError, farmer1.validate)