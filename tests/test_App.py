import json
import unittest
from dataserv.Farmer import db
from dataserv.app import app, secs_to_mins


class AppTest(unittest.TestCase):

    # setup and tear down
    def setUp(self):
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
        self.assertEqual(b"Registration Failed: Address Already Is Registered.", rv.data)
        self.assertEqual(rv.status_code, 409)

    def test_register_invalid(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc_this_is_not_an_address'
        rv = self.app.get('/api/register/{0}'.format(addr))

        self.assertEqual(b"Registration Failed: Invalid BTC Address.", rv.data)
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
        self.assertEqual(b"Ping Accepted.", rv.data)
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
        self.assertEqual(b"Ping Failed: Invalid BTC Address.", rv.data)
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

    # TODO: new contract call
    def test_new_contract(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        rv = self.app.get('/api/register/{0}'.format(addr))

         # good registration
        self.assertEqual(b"User registered.", rv.data)
        self.assertEqual(rv.status_code, 200)

        # grab a contract
        rv = self.app.get('/api/contract/new/{0}'.format(addr))
        self.assertEqual(rv.status_code, 200)
        json_data = json.loads(rv.data.decode("utf-8"))

        # check type 0 contracts
        self.assertEqual(json_data["btc_addr"], addr)
        self.assertEqual(json_data["contract-type"], 0)


    def test_new_contract_fail(self):
        addr1 = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        addr2 = 'notvalidaddress'

        # grab a contract with no farmer registered
        rv = self.app.get('/api/contract/new/{0}'.format(addr1))
        self.assertEqual(rv.status_code, 404)

        # grab a contract with invalid btc address
        rv = self.app.get('/api/contract/new/{0}'.format(addr2))
        self.assertEqual(rv.status_code, 400)