import unittest
from dataserv.app import db, app
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

        self.assertEqual(my_contract.btc_addr, addr)
        self.assertEqual(my_contract.contract_type, 0)
        self.assertEqual(my_contract.file_hash, '8366600f680255341531972a68f201c9edee89350e6d8c43c2c22a385bf02a60')
        self.assertEqual(my_contract.byte_size, 1024)
        self.assertEqual(my_contract.seed, 'ba17da75c580a0749b6c3d32')

    def test_new_contract2(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        my_contract = Contract()
        my_contract.new_contract(addr)
        self.assertEqual(my_contract.btc_addr, addr)
        self.assertEqual(my_contract.contract_type, 0)
        self.assertEqual(my_contract.byte_size, app.config["BYTE_SIZE"])

    def test_new_contract_json(self):
        addr = '191GVvAaTRxLmz3rW3nU5jAV1rF186VxQc'
        my_contract = Contract()
        my_contract.new_contract(addr, 'ba17da75c580a0749b6c3d32', 1024)
        json_contract = my_contract.to_json()

        self.assertEqual(json_contract["btc_addr"], addr)
        self.assertEqual(json_contract["contract_type"], 0)
        self.assertEqual(json_contract["file_hash"], '8366600f680255341531972a68f201c9edee89350e6d8c43c2c22a385bf02a60')
        self.assertEqual(json_contract["byte_size"], 1024)
        self.assertEqual(json_contract["seed"], 'ba17da75c580a0749b6c3d32')