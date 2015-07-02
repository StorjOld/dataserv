
import os
import hashlib
import binascii
import RandomIO
from dataserv.run import app, db


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btc_addr = db.Column(db.String(35))
    contract_type = db.Column(db.Integer, default=0)
    file_hash = db.Column(db.String(128))
    byte_size = db.Column(db.Integer, default=0)
    seed = db.Column(db.String(128), unique=True)

    def __init__(self, btc_addr):
        self.btc_addr = btc_addr

    def to_json(self):
        """JSON dump of the contract object."""
        contract_template = {
            "btc_addr": self.btc_addr,
            "contract_type": self.contract_type,
            "file_hash": self.file_hash,
            "byte_size": self.byte_size,
            "seed": self.seed
        }

        return contract_template

    def below_limit(self, limit=None):
        current_size = 0
        contracts = Contract.query.filter_by(btc_addr=self.btc_addr).all()
        for single_contract in contracts:
            current_size += single_contract.byte_size

        if limit is None:
            return current_size < app.config["BYTE_FARMER_MAX"]
        else:
            return current_size < limit

    def new_contract(self, seed=None, byte_size=None):
        """Build a new contract."""
        self.contract_type = 0

        # make sure that farmer can actually create new contracts
        if not self.below_limit():
            raise MemoryError("Contract Capacity Limit Reached.")

        # take in a seed, if not generate it ourselves
        if seed is None:
            seed = os.urandom(12)
            self.seed = binascii.hexlify(seed).decode('ascii')
        else:
            self.seed = seed

        # take in a byte_size, if not then get it from config
        if byte_size is None:
            self.byte_size = app.config["BYTE_SIZE"]
        else:
            self.byte_size = byte_size

        gen_file = RandomIO.RandomIO(seed).read(self.byte_size)
        self.file_hash = hashlib.sha256(gen_file).hexdigest()

        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def list_contracts(self):
        contracts = Contract.query.filter_by(btc_addr=self.btc_addr).all()
        json_contracts = []
        for contract in contracts:
            json_contracts.append(contract.to_json())

        payload_template = {
            "contracts": json_contracts
        }

        return payload_template
