import os
import hashlib
import binascii
import RandomIO
from dataserv.app import db, app


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btc_addr = db.Column(db.String(35), unique=True)
    contract_type = db.Column(db.Integer, default=0)
    file_hash = db.Column(db.String(128))
    byte_size = db.Column(db.Integer, default=0)
    seed = db.Column(db.String(128))

    def __init__(self):
        pass

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

    def new_contract(self, btc_addr, seed=None, byte_size=None):
        """Build a new contract."""
        self.btc_addr = btc_addr
        self.contract_type = 0

        # generate a random seed
        seed = os.urandom(12)
        self.seed = binascii.hexlify(seed).decode('ascii')

        self.byte_size = app.config["SHARD_SIZE"]
        gen_file = RandomIO.RandomIO(seed).read(self.byte_size)
        self.file_hash = hashlib.sha256(gen_file).hexdigest()
