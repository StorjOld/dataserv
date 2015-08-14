import hashlib
from dataserv.run import db
from datetime import datetime
from sqlalchemy import DateTime
from btctxstore import BtcTxStore


def sha256(content):
    """Finds the sha256 hash of the content."""
    content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btc_addr = db.Column(db.String(35), unique=True)

    last_seen = db.Column(DateTime, default=datetime.utcnow)
    height = db.Column(db.Integer, default=0)

    def __init__(self, btc_addr, last_seen=None):
        """
        A farmer is a un-trusted client that provides some disk space
        in exchange for payment. We use this object to keep track of
        farmers connected to this node.

        """
        self.blockchain = BtcTxStore()
        self.btc_addr = btc_addr
        self.last_seen = last_seen

    def __repr__(self):
        return '<Farmer BTC Address: %r>' % self.btc_addr

    def is_btc_address(self):
        """Check if the address is a valid Bitcoin public key."""
        return self.blockchain.validate_address(self.btc_addr)

    def validate(self, register=False):
        """Make sure this farmer fits the rules for this node."""
        # check if this is a valid BTC address or not
        if not self.is_btc_address():
            raise ValueError("Invalid BTC Address.")
        elif self.exists() and register:
            raise LookupError("Address Already Is Registered.")
        elif not self.exists() and not register:
            raise LookupError("Address Not Registered.")

    def register(self):
        """Add the farmer to the database."""
        self.validate(True)

        # If everything works correctly then commit to database.
        db.session.add(self)
        db.session.commit()

    def exists(self):
        """Check to see if this address is already listed."""
        query = db.session.query(Farmer.btc_addr)
        return query.filter(Farmer.btc_addr == self.btc_addr).count() > 0

    def lookup(self):
        """Return the Farmer object for the bitcoin address passed."""
        self.validate()
        farmer = Farmer.query.filter_by(btc_addr=self.btc_addr).first()
        return farmer

    def ping(self):
        """
        Keep-alive for the farmer. Validation can take a long time, so
        we just want to know if they are still there.

        """
        farmer = self.lookup()
        farmer.last_seen = datetime.utcnow()
        db.session.commit()

    # TODO: Actually do an audit.
    def audit(self):
        """
        Complete a cryptographic audit of files stored on the farmer. If
        the farmer completes an audit we also update when we last saw them.

        """
        self.ping()

    def set_height(self, height):
        """Set the farmers advertised height."""
        self.validate()

        self.ping()  # also serves as a valid ping
        farmer = self.lookup()
        farmer.height = height
        db.session.commit()

        return self.height
