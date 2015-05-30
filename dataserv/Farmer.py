from flask import Flask
from datetime import datetime
from sqlalchemy import DateTime
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/db/dataserv.db'
db = SQLAlchemy(app)


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

    def validate(self):
        # check if this is a valid BTC address or not
        if not self.is_btc_address():
            raise ValueError("Invalid BTC Address.")
        elif self.address_exists():
            raise ValueError("Address Already Is Registered.")

    def is_btc_address(self):
        """
        Does simple validation of a bitcoin-like address.
        Source: http://bit.ly/17OhFP5
        param : address : an ASCII or unicode string, of a bitcoin address.
        returns : boolean, indicating that the address has a correct format.
        """

        # The first character indicates the "version" of the address.
        chars_ok_first = "123"
        # alphanumeric characters without : l I O 0
        chars_ok = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

        # We do not check the high length limit of the address.
        # Usually, it is 35, but nobody knows what could happen in the future.
        if len(self.btc_addr) < 27:
            return False
        # Changed from the original code, we do want to check the upper bounds
        elif len(self.btc_addr) > 35:
            return False
        elif self.btc_addr[0] not in chars_ok_first:
            return False

        # We use the function "all" by passing it an enumerator as parameter.
        # It does a little optimization :
        # if one of the character is not valid, the next ones are not tested.
        return all((char in chars_ok for char in self.btc_addr[1:]))

    def register(self):
        """Add the farmer to the database."""

        # Make sure the farmer is even a valid address.
        # Later we will apply rule sets, like if the farmer has the
        # correct SJCX balance, reputation, etc.
        self.validate()

        # If everything works correctly then commit to database.
        db.session.add(self)
        db.session.commit()

    def address_exists(self):
        """Check to see if this address is already listed."""
        return db.session.query(Farmer.btc_addr).filter(Farmer.btc_addr==self.btc_addr).count() > 0