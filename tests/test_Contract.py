import unittest
from dataserv.app import db
from dataserv.Contract import Contract

class ContractTest(unittest.TestCase):

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_new_contract(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        my_contract = Contract()
        my_contract.new_contract(addr, 'ba17da75c580a0749b6c3d32', 1024)
        print(my_contract.to_json())
