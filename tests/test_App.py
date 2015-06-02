import unittest
from dataserv.app import app
from dataserv.Farmer import db


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_hello_world(self):
        rv = self.app.get('/')
        self.assertEqual(b"Hello World.", rv.data)

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

        # good registration
        self.assertEqual(b"Registration Failed: Invalid BTC Address.", rv.data)
        self.assertEqual(rv.status_code, 400)

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

    def test_ping_bad(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        # no registration

        # now test ping
        rv = self.app.get('/api/ping/{0}'.format(addr))

        # good ping
        self.assertEqual(b"Ping Failed: Farmer not found.", rv.data)
        self.assertEqual(rv.status_code, 404)