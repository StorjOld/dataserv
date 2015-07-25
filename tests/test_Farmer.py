import json
import unittest
from dataserv.app import db
from dataserv.Farmer import sha256
from dataserv.Farmer import Farmer


class FarmerTest(unittest.TestCase):

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_address_error(self):
        addr1 = 'not valid address'
        farmer1 = Farmer(addr1)
        self.assertRaises(ValueError, farmer1.validate)

    def test_repr(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        farmer = Farmer(addr)
        ans = "<Farmer BTC Address: '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'>"
        self.assertEqual(repr(farmer), ans)

    def test_register(self):
        addr1 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        addr2 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc9999ghjfghj99'
        addr3 = 'not valid address'

        farmer1 = Farmer(addr1)
        farmer2 = Farmer(addr2)
        farmer3 = Farmer(addr3)

        self.assertFalse(farmer1.exists())
        farmer1.register()
        self.assertTrue(farmer1.exists())

        # test duplicate
        self.assertRaises(LookupError, farmer1.register)

        # these should not be inserted
        self.assertRaises(ValueError, farmer2.register)
        self.assertRaises(ValueError, farmer3.register)

        # double check they are not in the db
        self.assertFalse(farmer2.exists())
        self.assertFalse(farmer3.exists())

    def test_ping(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        farmer = Farmer(addr)
        farmer.register()

        register_time = farmer.last_seen
        farmer.ping()  # update last seen
        ping_time = farmer.last_seen
        audit_time = farmer.last_audit

        self.assertTrue(register_time < ping_time)
        # ping time should always be more recent or equal to audit time
        self.assertTrue(ping_time >= audit_time)

    def test_ping_failed(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        farmer = Farmer(addr)
        # we don't actually register it this time

        self.assertRaises(LookupError, farmer.ping)

    def test_audit(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        farmer = Farmer(addr)
        farmer.register()

        register_time = farmer.last_seen
        farmer.audit()
        ping_time = farmer.last_seen
        audit_time = farmer.last_audit

        self.assertTrue(register_time < ping_time)
        # ping time should always be more recent or equal to audit time
        self.assertTrue(ping_time >= audit_time)

    def test_audit_failed(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        farmer = Farmer(addr)
        # we don't actually register it this time

        self.assertRaises(LookupError, farmer.audit)

    def test_sha256(self):
        ans = 'c059c8035bbd74aa81f4c787c39390b57b974ec9af25a7248c46a3ebfe0f9dc8'
        self.assertEqual(sha256("storj"), ans)
        self.assertNotEqual(sha256("not storj"), ans)
