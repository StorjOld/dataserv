import json
import unittest
from time import mktime
from datetime import datetime
from dataserv.run import app, db
from btctxstore import BtcTxStore
from email.utils import formatdate
from dataserv.app import secs_to_mins, online_farmers

# FIXME generate addresses with btctxstore
fixtures = json.load(open("tests/fixtures.json"))
addresses = fixtures["addresses"]


class TemplateTest(unittest.TestCase):
    def setUp(self):
        app.config["SKIP_AUTHENTICATION"] = True  # monkey patch
        app.config["DISABLE_CACHING"] = True

        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class RegisterTest(TemplateTest):

    def test_register(self):
        rv = self.app.get('/api/register/{0}/{1}'.format(addresses["alpha"],
                                                         addresses["beta"]))

        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(addresses["alpha"], data["btc_addr"])
        self.assertEqual(addresses["beta"], data["payout_addr"])
        self.assertEqual(rv.status_code, 200)

    def test_register_no_payout(self):
        rv = self.app.get('/api/register/{0}'.format(addresses["gamma"]))

        # good registration
        return_data = json.loads(rv.data.decode("utf-8"))
        expected_data = {
            "height": 0,
            "btc_addr": addresses["gamma"],
            'payout_addr': addresses["gamma"],
            "last_seen": 0
        }
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(return_data, expected_data)

        # duplicate registration
        rv = self.app.get('/api/register/{0}'.format(addresses["gamma"]))
        self.assertEqual(b"Registration Failed: Address already is registered."
                         , rv.data)
        self.assertEqual(rv.status_code, 409)

    def test_register_w_payout(self):
        rv = self.app.get('/api/register/{0}/{1}'.format(addresses["delta"],
                                                         addresses["epsilon"]))
        # good registration
        return_data = json.loads(rv.data.decode("utf-8"))
        expected_data = {
            "height": 0,
            "btc_addr": addresses["delta"],
            'payout_addr': addresses["epsilon"],
            "last_seen": 0
        }
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(return_data, expected_data)

        # duplicate registration
        rv = self.app.get('/api/register/{0}/{1}'.format(addresses["delta"],
                                                         addresses["epsilon"]))
        self.assertEqual(b"Registration Failed: Address already is registered."
                         , rv.data)
        self.assertEqual(rv.status_code, 409)

        # duplicate payout address is ok
        rv = self.app.get('/api/register/{0}/{1}'.format(addresses["zeta"],
                                                         addresses["epsilon"]))
        return_data = json.loads(rv.data.decode("utf-8"))
        expected_data = {
            "height": 0,
            "btc_addr": addresses["zeta"],
            'payout_addr': addresses["epsilon"],
            "last_seen": 0
        }
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(return_data, expected_data)

    def test_register_invalid_address(self):
        # bad address only
        rv = self.app.get('/api/register/{0}'.format(addresses["omega"]))
        self.assertEqual(b"Registration Failed: Invalid Bitcoin address.",
                         rv.data)
        self.assertEqual(rv.status_code, 400)

        # good address, bad address
        rv = self.app.get('/api/register/{0}/{1}'.format(addresses["eta"],
                                                         addresses["omega"]))
        self.assertEqual(b"Registration Failed: Invalid Bitcoin address.",
                         rv.data)
        self.assertEqual(rv.status_code, 400)

        # bad address, good address
        rv = self.app.get('/api/register/{0}/{1}'.format(addresses["omega"],
                                                         addresses["theta"]))
        self.assertEqual(b"Registration Failed: Invalid Bitcoin address.",
                         rv.data)
        self.assertEqual(rv.status_code, 400)


class PingTest(TemplateTest):

    def test_ping_good(self):
        rv = self.app.get('/api/register/{0}'.format(addresses["alpha"]))
        self.assertEqual(rv.status_code, 200)

        # now test ping
        rv = self.app.get('/api/ping/{0}'.format(addresses["alpha"]))

        # good ping
        self.assertEqual(b"Ping accepted.", rv.data)
        self.assertEqual(rv.status_code, 200)

    def test_ping_not_found(self):
        # now test ping with no registration
        rv = self.app.get('/api/ping/{0}'.format(addresses["beta"]))

        # bad ping
        self.assertEqual(b"Ping Failed: Farmer not found.", rv.data)
        self.assertEqual(rv.status_code, 404)

    def test_ping_invalid_address(self):
        # now test ping with no registration and invalid address
        rv = self.app.get('/api/ping/{0}'.format(addresses["omega"]))

        # bad ping
        self.assertEqual(b"Ping Failed: Invalid Bitcoin address.", rv.data)
        self.assertEqual(rv.status_code, 400)



class OnlineTest(TemplateTest):

    def test_online(self):
        rv = self.app.get('/api/register/{0}'.format(addresses["alpha"]))
        self.assertEqual(rv.status_code, 200)

        # now test ping
        self.app.get('/api/ping/{0}'.format(addresses["alpha"]))

        # get online data
        rv = self.app.get('/api/online')

        # see if that address is in the online status
        self.assertTrue(addresses["alpha"] in str(rv.data))

    def test_farmer_json(self):  # test could be better
        rv = self.app.get('/api/register/{0}'.format(addresses["beta"]))
        self.assertEqual(rv.status_code, 200)

        # get online json data
        rv = self.app.get('/api/online/json')
        self.assertTrue(addresses["beta"] in str(rv.data))

    def test_farmer_order(self):
        addr1 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        addr2 = '18c2qnUAfgF3UnJCjAz2rpWQph5xugEfkr'
        addr3 = '1NqtfdHe3X6rqHRQjsGq5CT9LYYjTFJ1qD'

        # register farmers
        self.app.get('/api/register/{0}'.format(addr1))
        self.app.get('/api/register/{0}'.format(addr2))
        self.app.get('/api/register/{0}'.format(addr3))

        # set height
        self.app.get('/api/height/{0}/{1}'.format(addr1, 0))
        self.app.get('/api/height/{0}/{1}'.format(addr2, 2475))
        self.app.get('/api/height/{0}/{1}'.format(addr3, 2525))

        # get farmers
        farmers = online_farmers()
        self.assertEqual(farmers[0].btc_addr, addr3)
        self.assertEqual(farmers[1].btc_addr, addr2)
        self.assertEqual(farmers[2].btc_addr, addr1)

        # set height
        self.app.get('/api/height/{0}/{1}'.format(addr1, 5000))

        # get farmers
        farmers = online_farmers()
        self.assertEqual(farmers[0].btc_addr, addr1)


class HeightTest(TemplateTest):

    def test_farmer_set_height(self):
        # not found
        rv = self.app.get('/api/height/{0}/1'.format(addresses["beta"]))
        self.assertEqual(rv.status_code, 404)

        # register farmer
        self.app.get('/api/register/{0}'.format(addresses["beta"]))

        # correct
        rv = self.app.get('/api/height/{0}/5'.format(addresses["beta"]))
        self.assertEqual(rv.status_code, 200)
        rv = self.app.get('/api/online'.format(addresses["beta"]))
        self.assertTrue(b"5" in rv.data)

        # invalid btc address
        rv = self.app.get('/api/height/{0}/1'.format(addresses["omega"]))
        self.assertEqual(rv.status_code, 400)

    def test_height_limit(self):
        self.app.get('/api/register/{0}'.format(addresses["gamma"]))

        # set height 50
        self.app.get('/api/height/{0}/{1}'.format(addresses["gamma"], 50))
        rv = self.app.get('/api/online')
        self.assertTrue(b"50" in rv.data)

        # set a crazy height
        rv = self.app.get('/api/height/{0}/{1}'.format(addresses["gamma"],
                                                       250000))
        self.assertEqual(rv.status_code, 413)


class AppAuthenticationHeadersTest(unittest.TestCase):

    def setUp(self):
        app.config["SKIP_AUTHENTICATION"] = False  # monkey patch
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_success(self):
        blockchain = BtcTxStore()
        wif = blockchain.create_key()
        address = blockchain.get_address(wif)

        # create header date and authorization signature
        header_date = formatdate(timeval=mktime(datetime.now().timetuple()),
                                 localtime=True, usegmt=True)
        message = app.config["ADDRESS"] + " " + header_date
        header_authorization = blockchain.sign_unicode(wif, message)

        headers = {"Date": header_date, "Authorization": header_authorization}
        url = '/api/register/{0}'.format(address)
        rv = self.app.get(url, headers=headers)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(address, data["btc_addr"])
        self.assertEqual(rv.status_code, 200)

    def test_fail(self):
        rv = self.app.get('/api/register/{0}'.format(addresses["eta"]))
        self.assertEqual(rv.status_code, 401)

        rv = self.app.get('/api/ping/{0}'.format(addresses["eta"]))
        self.assertEqual(rv.status_code, 401)

        rv = self.app.get('/api/height/{0}/10'.format(addresses["eta"]))
        self.assertEqual(rv.status_code, 401)


class MiscAppTest(TemplateTest):

    # making sure that at least the web server works
    def test_hello_world(self):
        rv = self.app.get('/')
        self.assertEqual(b"Hello World.", rv.data)

    # time helper
    def test_helper_time(self):
        time1 = 15
        time2 = 75
        time3 = 4000

        self.assertEqual(secs_to_mins(time1), "15 second(s)")
        self.assertEqual(secs_to_mins(time2), "1 minute(s)")
        self.assertEqual(secs_to_mins(time3), "1 hour(s)")

    # total bytes call
    def test_farmer_total_bytes(self):
        addr1 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        addr2 = '18c2qnUAfgF3UnJCjAz2rpWQph5xugEfkr'
        addr3 = '1NqtfdHe3X6rqHRQjsGq5CT9LYYjTFJ1qD'
        addr4 = '1JnaPB29Un3FBSf3e4Jzabwi1ekeKoh1Gr'

        # register farmers
        self.app.get('/api/register/{0}'.format(addr1))
        self.app.get('/api/register/{0}'.format(addr2))
        self.app.get('/api/register/{0}'.format(addr3))
        self.app.get('/api/register/{0}'.format(addr4))

        # set height
        self.app.get('/api/height/{0}/{1}'.format(addr1, 0))
        self.app.get('/api/height/{0}/{1}'.format(addr2, 2475))
        self.app.get('/api/height/{0}/{1}'.format(addr3, 2525))
        self.app.get('/api/height/{0}/{1}'.format(addr4, 5000))

        # check online
        rv = self.app.get('/api/online')
        self.assertTrue(b"0" in rv.data)
        self.assertTrue(b"2475" in rv.data)
        self.assertTrue(b"2525" in rv.data)
        self.assertTrue(b"5000" in rv.data)

        # check total bytes
        rv = self.app.get('/api/total')
        self.assertTrue(b'"total_TB": 1.22' in rv.data)
        self.assertTrue(b'"total_farmers": 4' in rv.data)

    def test_get_address(self):
        rv = self.app.get('/api/address')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode("utf-8"))
        self.assertEqual(app.config["ADDRESS"], data["address"])
