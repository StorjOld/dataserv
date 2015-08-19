import unittest
from dataserv.run import app, db
from dataserv.app import secs_to_mins, online_farmers


class AppTest(unittest.TestCase):

    # setup
    def setUp(self):
        app.config["SKIP_AUTHENTICATION"] = True  # monkey patch
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # simple index test
    def test_hello_world(self):
        rv = self.app.get('/')
        self.assertEqual(b"Hello World.", rv.data)

    # register call
    def test_register(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        rv = self.app.get('/api/register/{0}'.format(addr))

        # good registration
        self.assertEqual(b"User registered.", rv.data)
        self.assertEqual(rv.status_code, 200)

        # duplicate registration
        rv = self.app.get('/api/register/{0}'.format(addr))
        self.assertEqual(b"Registration Failed: Address already is registered.", rv.data)
        self.assertEqual(rv.status_code, 409)

    def test_register_invalid_address(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc_this_is_not_an_address'
        rv = self.app.get('/api/register/{0}'.format(addr))

        # invalid address
        self.assertEqual(b"Registration Failed: Invalid Bitcoin address.", rv.data)
        self.assertEqual(rv.status_code, 400)

    # ping call
    def test_ping_good(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        rv = self.app.get('/api/register/{0}'.format(addr))

        # good registration
        self.assertEqual(b"User registered.", rv.data)
        self.assertEqual(rv.status_code, 200)

        # now test ping
        rv = self.app.get('/api/ping/{0}'.format(addr))

        # good ping
        self.assertEqual(b"Ping accepted.", rv.data)
        self.assertEqual(rv.status_code, 200)

    def test_ping_not_found(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        # no registration

        # now test ping
        rv = self.app.get('/api/ping/{0}'.format(addr))

        # good ping
        self.assertEqual(b"Ping Failed: Farmer not found.", rv.data)
        self.assertEqual(rv.status_code, 404)

    def test_ping_invalid_address(self):
        addr = 'notvalidaddress'

        # now test ping
        rv = self.app.get('/api/ping/{0}'.format(addr))

        # good ping
        self.assertEqual(b"Ping Failed: Invalid Bitcoin address.", rv.data)
        self.assertEqual(rv.status_code, 400)

    # time helper
    def test_helper_time(self):
        time1 = 15
        time2 = 75
        time3 = 4000

        self.assertEqual(secs_to_mins(time1), "15 second(s)")
        self.assertEqual(secs_to_mins(time2), "1 minute(s)")
        self.assertEqual(secs_to_mins(time3), "1 hour(s)")

    # online call
    def test_online(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        rv = self.app.get('/api/register/{0}'.format(addr))

        # good registration
        self.assertEqual(b"User registered.", rv.data)
        self.assertEqual(rv.status_code, 200)

        # now test ping
        self.app.get('/api/ping/{0}'.format(addr))

        # get online data
        rv = self.app.get('/api/online')

        # see if that address is in the online status
        self.assertTrue(addr in str(rv.data))

    def test_farmer_set_height(self):
        addr1 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        addr2 = 'notvalidaddress'

        # not found
        rv = self.app.get('/api/height/{0}/1'.format(addr1))
        self.assertEqual(rv.status_code, 404)

        # register farmer
        self.app.get('/api/register/{0}'.format(addr1))

        # correct
        rv = self.app.get('/api/height/{0}/5'.format(addr1))
        self.assertEqual(rv.status_code, 200)
        rv = self.app.get('/api/online'.format(addr1))
        self.assertTrue(b"5" in rv.data)

        # invalid btc address
        rv = self.app.get('/api/height/{0}/1'.format(addr2))
        self.assertEqual(rv.status_code, 400)

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
        json_data =  b'"total_TB": 1.22\n}'

        self.assertTrue(json_data in  rv.data)

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
