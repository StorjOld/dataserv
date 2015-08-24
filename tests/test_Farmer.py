import json
import unittest
from btctxstore import BtcTxStore
from dataserv.app import db, app
from dataserv.Farmer import sha256
from dataserv.Farmer import Farmer
from email.utils import formatdate
from datetime import datetime
from datetime import timedelta
from time import mktime


class FarmerTest(unittest.TestCase):

    def setUp(self):
        app.config["SKIP_AUTHENTICATION"] = True  # monkey patch
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_repr(self):
        farmer = Farmer('191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc')
        ans = "<Farmer BTC Address: '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'>"
        self.assertEqual(repr(farmer), ans)

    def test_sha256(self):
        ans = 'c059c8035bbd74aa81f4c787c39390b57b974ec9af25a7248c46a3ebfe0f9dc8'
        self.assertEqual(sha256("storj"), ans)
        self.assertNotEqual(sha256("not storj"), ans)

    def test_register(self):
        addr1 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        addr2 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc9999ghjfghj99'
        addr3 = 'not valid address'

        # test success
        farmer1 = Farmer(addr1)
        self.assertFalse(farmer1.exists())
        farmer1.register()
        self.assertTrue(farmer1.exists())

        # test duplicate error
        self.assertRaises(LookupError, farmer1.register)

        def callback_a():
            Farmer(addr2)
        self.assertRaises(ValueError, callback_a)

        def callback_b():
            Farmer(addr3)
        self.assertRaises(ValueError, callback_b)

    def test_ping(self):
        farmer = Farmer('191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc')

        # test ping before registration
        self.assertRaises(LookupError, farmer.ping)

        # register farmer
        farmer.register()

        # get register time, and make sure the ping work
        register_time = farmer.last_seen
        farmer.ping()  # update last seen
        ping_time = farmer.last_seen
        self.assertTrue(register_time < ping_time)

    def test_height(self):
        farmer = Farmer('191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc')
        farmer.register()

        # set height and check function output
        self.assertEqual(farmer.height, 0)
        self.assertEqual(farmer.set_height(5), 5)
        self.assertEqual(farmer.height, 5)

        # check the db object as well
        farmer2 = farmer.lookup()
        self.assertEqual(farmer2.height, 5)

    def test_audit(self):
        farmer = Farmer('191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc')

        # test audit before registration
        self.assertRaises(LookupError, farmer.audit)

        # register farmer
        farmer.register()

        # get register time, and make sure the ping work
        register_time = farmer.last_seen
        farmer.audit()
        ping_time = farmer.last_seen
        self.assertTrue(register_time < ping_time)

    def test_to_json(self):
        farmer = Farmer('191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc')
        farmer.register()

        farmer.ping()
        farmer.set_height(50)

        test_json = {
            "height": 50,
            "btc_addr": "191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc",
            'payout_addr': '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc',
            "last_seen": 0
        }
        call_payload = json.loads(farmer.to_json())
        self.assertEqual(test_json, call_payload)


class FarmerAuthenticationTest(unittest.TestCase):

    def setUp(self):
        app.config["SKIP_AUTHENTICATION"] = False  # monkey patch
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_authentication_success(self):
        blockchain = BtcTxStore()
        wif = blockchain.create_key()
        address = blockchain.get_address(wif)
        farmer = Farmer(address)

        header_date = formatdate(timeval=mktime(datetime.now().timetuple()),
                                 localtime=True, usegmt=True)
        message = farmer.get_server_address() + " " + header_date
        header_authorization = blockchain.sign_unicode(wif, message)
        self.assertTrue(farmer.authenticate(header_authorization, header_date))

    def test_authentication_timeout(self):
        def callback():
            blockchain = BtcTxStore()
            wif = blockchain.create_key()
            address = blockchain.get_address(wif)
            farmer = Farmer(address)

            timeout = farmer.get_server_authentication_timeout()

            date = datetime.now() - timedelta(seconds=timeout)
            header_date = formatdate(timeval=mktime(date.timetuple()),
                                     localtime=True, usegmt=True)
            message = farmer.get_server_address() + " " + header_date
            header_authorization = blockchain.sign_unicode(wif, message)
            farmer.authenticate(header_authorization, header_date)
        self.assertRaises(PermissionError, callback)

    # TODO test incorrect address
    # TODO test incorrect signature
