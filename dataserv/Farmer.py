import hashlib
from flask import Flask
from datetime import datetime
from sqlalchemy import DateTime
from dataserv.Challenge import Challenge
from flask.ext.sqlalchemy import SQLAlchemy
from dataserv.Validator import is_btc_address


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dataserv.db'
app.config['SEED_HEIGHT'] = 100
app.config['DATA_DIR'] = 'data/'
app.config['SHARD_SIZE'] = 10*1024*1024  # 10 MB
db = SQLAlchemy(app)


def sha256(content):
    """Finds the sha256 hash of the content."""
    content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btc_addr = db.Column(db.String(35), unique=True)

    last_seen = db.Column(DateTime, default=datetime.utcnow)
    last_audit = db.Column(DateTime, default=datetime.utcnow)

    seed = db.Column(db.Integer)
    response = db.Column(db.String(128))

    def __init__(self, btc_addr, last_seen=None, last_audit=None):
        """
        A farmer is a un-trusted client that provides some disk space
        in exchange for payment.

        """

        self.btc_addr = btc_addr
        self.last_seen = last_seen
        self.last_audit = last_audit
        self.seed = None
        self.response = None

    def __repr__(self):
        return '<Farmer BTC Address: %r>' % self.btc_addr

    def is_btc_address(self):
        return is_btc_address(self.btc_addr)

    def validate(self):
        """Make sure this farmer fits the rules for this node."""
        # check if this is a valid BTC address or not
        if not self.is_btc_address():
            raise ValueError("Invalid BTC Address.")
        elif self.exists():
            raise LookupError("Address Already Is Registered.")

    def register(self):
        """Add the farmer to the database."""

        # Make sure the farmer is even a valid address.
        # Later we will apply rule sets, like if the farmer has the
        # correct SJCX balance, reputation, etc.
        self.validate()

        # If everything works correctly then commit to database.
        db.session.add(self)
        db.session.commit()

    def exists(self):
        """Check to see if this address is already listed."""
        return db.session.query(Farmer.btc_addr).filter(Farmer.btc_addr == self.btc_addr).count() > 0

    def ping(self):
        """
        Keep alive for the farmer. Validation can take a long time, so
        we just want to know if they are still there.
        """
        if not self.is_btc_address():
            raise ValueError("Invalid address.")

        farmer = Farmer.query.filter_by(btc_addr=self.btc_addr).first()

        if farmer is not None:
            farmer.last_seen = datetime.utcnow()
            db.session.commit()
        else:
            raise LookupError("Farmer not found.")

        return farmer

    def gen_challenge(self):
        """Generate a random challenge to insert into the database."""
        chal = Challenge(self.btc_addr, app.config['SEED_HEIGHT'], app.config['SHARD_SIZE'])
        self.seed, self.response = chal.gen_challenge(app.config['DATA_DIR'])
        print(self.seed, self.response)
