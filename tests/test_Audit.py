import unittest
from dataserv.Audit import Audit
from dataserv.app import db, app
from btctxstore import BtcTxStore
from dataserv.Farmer import Farmer
import binascii
from pycoin.encoding import a2b_hashed_base58


def addr2nodeid(addr):
    return binascii.hexlify(a2b_hashed_base58(addr)[1:]).decode("utf-8")


class AuditTest(unittest.TestCase):

    def setUp(self):
        app.config["SKIP_AUTHENTICATION"] = True  # monkey patch
        app.config["DISABLE_CACHING"] = True

        self.btctxstore = BtcTxStore()
        self.bad_addr = 'notvalidaddress'

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def gen_btc_addr(self):
        return self.btctxstore.get_address(self.btctxstore.get_key(
                                self.btctxstore.create_wallet()))

    def test_register_audit(self):
        btc_addr = self.gen_btc_addr()
        btc_addr2 = self.gen_btc_addr()
        nodeid = addr2nodeid(btc_addr)
        nodeid2 = addr2nodeid(btc_addr2)

        # register farmer and test db
        farmer1 = Farmer(nodeid)
        self.assertFalse(farmer1.exists())
        farmer1.register(btc_addr)
        self.assertTrue(farmer1.exists())

        # do callbacks to properly test errors
        def callback_a():
            Audit(self.bad_addr, 0)

        def callback_b():
            Audit(nodeid2, 0)

        audit = Audit(nodeid, 0)
        self.assertFalse(audit.exists())
        audit.save()
        audit2 = Audit(nodeid, 0)
        self.assertTrue(audit2.exists())

        def callback_c():
            Audit(nodeid, 1, 'invalid_sha')

        self.assertRaises(ValueError, callback_a)
        self.assertRaises(LookupError, callback_b)
        self.assertRaises(TypeError, callback_c)

    def test_lookup(self):
        btc_addr = self.gen_btc_addr()
        nodeid = addr2nodeid(btc_addr)
        Farmer(nodeid).register(btc_addr)

        audit = Audit(nodeid, 0)
        audit.save()

        def callback_a():
            Audit(nodeid, 1).lookup()

        self.assertRaises(LookupError, callback_a)

        audit2 = Audit(nodeid, 0).lookup()
        audit3 = Audit(nodeid, 0)
        self.assertEqual(audit2, audit3)
