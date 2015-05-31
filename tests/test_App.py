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