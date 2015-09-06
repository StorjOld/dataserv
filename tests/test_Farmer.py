import time
import json
import unittest
from time import mktime
from datetime import datetime
from datetime import timedelta
from dataserv.app import db, app
from btctxstore import BtcTxStore
from email.utils import formatdate
from dataserv.Farmer import sha256
from dataserv.Farmer import Farmer, AuthError


# load address from fixtures file
fixtures = json.load(open("tests/fixtures.json"))
addresses = fixtures["addresses"]


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
        # test success
        farmer1 = Farmer(addresses["alpha"])
        self.assertFalse(farmer1.exists())
        farmer1.register()
        self.assertTrue(farmer1.exists())

        # test duplicate error
        self.assertRaises(LookupError, farmer1.register)

        def callback_a():
            Farmer(addresses["omega"])
        self.assertRaises(ValueError, callback_a)

    def test_ping(self):
        farmer = Farmer(addresses["beta"])

        # test ping before registration
        self.assertRaises(LookupError, farmer.ping)

        # register farmer
        farmer.register()

        # get register time, and make sure the ping work
        register_time = farmer.last_seen
        time.sleep(app.config["MAX_PING"] + 1) # ping faster than max_ping would be ignored
        farmer.ping()  # update last seen
        ping_time = farmer.last_seen
        self.assertTrue(register_time < ping_time)

    def test_ping_time_limit(self):
        farmer = Farmer(addresses["beta"])
        farmer.register()

        register_time = farmer.last_seen
        time.sleep(2)
        farmer.ping()

        # should still be around 0
        delta_seconds = int((farmer.last_seen - register_time).seconds)
        self.assertEqual(delta_seconds, 0)

    def test_height(self):
        farmer = Farmer(addresses["gamma"])
        farmer.register()

        # set height and check function output
        self.assertEqual(farmer.height, 0)
        self.assertEqual(farmer.set_height(5), 5)
        self.assertEqual(farmer.height, 5)

        # check the db object as well
        farmer2 = farmer.lookup()
        self.assertEqual(farmer2.height, 5)

    def test_audit(self):
        farmer = Farmer(addresses["delta"])

        # test audit before registration
        self.assertRaises(LookupError, farmer.audit)

        # register farmer
        farmer.register()

        # get register time, and make sure the ping work
        register_time = farmer.last_seen
        time.sleep(app.config["MAX_PING"] + 1) # ping faster than max_ping would be ignored
        farmer.audit()
        ping_time = farmer.last_seen
        self.assertTrue(register_time < ping_time)

    def test_to_json(self):
        farmer = Farmer(addresses["epsilon"])
        farmer.register()

        farmer.ping()
        farmer.set_height(50)

        test_json = {
            "height": 50,
            "btc_addr": addresses["epsilon"],
            'payout_addr': addresses["epsilon"],
            "last_seen": 0
        }
        call_payload = json.loads(farmer.to_json())
        self.assertEqual(test_json, call_payload)

    def test_auth_error(self):
        try:
            raise AuthError("Test Error")
        except AuthError as e:
            self.assertEqual(str(e), "'Test Error'")


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

    def test_authentication_timeout_success(self):
        blockchain = BtcTxStore()
        wif = blockchain.create_key()
        address = blockchain.get_address(wif)
        farmer = Farmer(address)

        timeout = farmer.get_server_authentication_timeout() - 2

        date = datetime.now() - timedelta(seconds=timeout)
        header_date = formatdate(timeval=mktime(date.timetuple()),
                                 localtime=True, usegmt=True)
        message = farmer.get_server_address() + " " + header_date
        header_authorization = blockchain.sign_unicode(wif, message)
        self.assertTrue(farmer.authenticate(header_authorization, header_date))

    def test_authentication_timeout_future_success(self):
        blockchain = BtcTxStore()
        wif = blockchain.create_key()
        address = blockchain.get_address(wif)
        farmer = Farmer(address)

        timeout = farmer.get_server_authentication_timeout() - 2

        date = datetime.now() + timedelta(seconds=timeout)
        header_date = formatdate(timeval=mktime(date.timetuple()),
                                 localtime=True, usegmt=True)
        message = farmer.get_server_address() + " " + header_date
        header_authorization = blockchain.sign_unicode(wif, message)
        self.assertTrue(farmer.authenticate(header_authorization, header_date))

    def test_authentication_no_date(self):
        def callback():
            blockchain = BtcTxStore()
            wif = blockchain.create_key()
            address = blockchain.get_address(wif)
            farmer = Farmer(address)

            header_date = formatdate(timeval=mktime(datetime.now().timetuple()),
                                     localtime=True, usegmt=True)
            message = farmer.get_server_address() + " " + header_date
            header_authorization = blockchain.sign_unicode(wif, message)
            farmer.authenticate(header_authorization, None)
        self.assertRaises(AuthError, callback)

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
        self.assertRaises(AuthError, callback)

    def test_authentication_day_timeout(self):
        def callback():
            blockchain = BtcTxStore()
            wif = blockchain.create_key()
            address = blockchain.get_address(wif)
            farmer = Farmer(address)

            date = datetime.now() - timedelta(days=1)
            header_date = formatdate(timeval=mktime(date.timetuple()),
                                     localtime=True, usegmt=True)
            message = farmer.get_server_address() + " " + header_date
            header_authorization = blockchain.sign_unicode(wif, message)
            farmer.authenticate(header_authorization, header_date)
        self.assertRaises(AuthError, callback)

    # TODO test incorrect address

    def test_authentication_bad_sig(self):
        def callback():
            blockchain = BtcTxStore()
            wif = blockchain.create_key()
            address = blockchain.get_address(wif)
            farmer = Farmer(address)

            header_date = formatdate(timeval=mktime(datetime.now().timetuple()),
                                     localtime=True, usegmt=True)
            header_authorization = blockchain.sign_unicode(wif, "lalala-wrong")
            farmer.authenticate(header_authorization, header_date)
        self.assertRaises(AuthError, callback)
