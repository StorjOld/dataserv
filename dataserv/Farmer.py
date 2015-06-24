import hashlib
from dataserv.app2 import db
from datetime import datetime
from sqlalchemy import DateTime
from dataserv.Contract import Contract
from dataserv.Validator import is_btc_address


def sha256(content):
    """Finds the sha256 hash of the content."""
    content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btc_addr = db.Column(db.String(35), unique=True)

    last_seen = db.Column(DateTime, default=datetime.utcnow)
    last_audit = db.Column(DateTime, default=datetime.utcnow)

    def __init__(self, btc_addr, last_seen=None, last_audit=None):
        """
        A farmer is a un-trusted client that provides some disk space
        in exchange for payment.

        """

        self.btc_addr = btc_addr
        self.last_seen = last_seen
        self.last_audit = last_audit

    def __repr__(self):
        return '<Farmer BTC Address: %r>' % self.btc_addr

    def is_btc_address(self):
        return is_btc_address(self.btc_addr)

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

        # Make sure the farmer is even a valid address.
        # Later we will apply rule sets, like if the farmer has the
        # correct SJCX balance, reputation, etc.
        self.validate(True)

        # If everything works correctly then commit to database.
        db.session.add(self)
        db.session.commit()

    def exists(self):
        """Check to see if this address is already listed."""
        query = db.session.query(Farmer.btc_addr)
        return query.filter(Farmer.btc_addr == self.btc_addr).count() > 0

    def lookup(self):
        self.validate()
        farmer = Farmer.query.filter_by(btc_addr=self.btc_addr).first()
        return farmer

    def update_time(self, ping=False, audit=False):
        """Update last_seen and last_audit for each farmer."""
        farmer = self.lookup()

        now = datetime.utcnow()
        if ping:
            farmer.last_seen = now
        if audit:
            farmer.last_audit = now
        db.session.commit()

    def ping(self):
        """
        Keep-alive for the farmer. Validation can take a long time, so
        we just want to know if they are still there.
        """
        self.update_time(True)

    # TODO: Actually do an audit.
    def audit(self):
        """
        Complete a cryptographic audit of files stored on the farmer. If
        the farmer completes an audit we also update when we last saw them.
        """
        self.update_time(True, True)

    def new_contract(self, seed=None):
        self.lookup()

        con = Contract(self.btc_addr)
        con.new_contract(seed)
        return con.to_json()
