import json
import hashlib
from email.utils import parsedate
from dataserv.run import db, app
from datetime import datetime
from datetime import timedelta
from sqlalchemy import DateTime
from btctxstore import BtcTxStore
from dataserv.Validator import is_btc_address


class AuthError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def sha256(content):
    """Finds the sha256 hash of the content."""
    content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btc_addr = db.Column(db.String(35), unique=True)
    payout_addr = db.Column(db.String(35))
    last_seen = db.Column(DateTime, default=datetime.utcnow)
    height = db.Column(db.Integer, default=0)

    def __init__(self, btc_addr, last_seen=None):
        """
        A farmer is a un-trusted client that provides some disk space
        in exchange for payment. We use this object to keep track of
        farmers connected to this node.

        """
        if not is_btc_address(btc_addr):
            raise ValueError("Invalid BTC Address.")
        self.btc_addr = btc_addr
        self.last_seen = last_seen

    def __repr__(self):
        return '<Farmer BTC Address: %r>' % self.btc_addr

    @staticmethod
    def get_server_address():
        return app.config["ADDRESS"]

    @staticmethod
    def get_server_authentication_timeout():
        return app.config["AUTHENTICATION_TIMEOUT"]

    def authenticate(self, header_authorization, header_date):
        if app.config["SKIP_AUTHENTICATION"]:
            return True
        if not header_authorization:
            raise AuthError("Header authorization required!")
        if not header_date:
            raise AuthError("Header date required!")

        # verify date
        date = datetime(*parsedate(header_date)[:6])
        timeout = self.get_server_authentication_timeout()
        delta = datetime.now() - date
        if delta >= timedelta(seconds=timeout):
            raise AuthError("Header date to old!")

        # verify signature
        message = self.get_server_address() + " " + header_date
        if not BtcTxStore().verify_signature_unicode(self.btc_addr,
                                                     header_authorization,
                                                     message):
            raise AuthError("Invalid header_authorization!")
        return True

    def validate(self, registering=False):
        """Make sure this farmer fits the rules for this node."""
        # check if this is a valid BTC address or not
        if not is_btc_address(self.payout_addr):
            print("hello")
            raise ValueError("Invalid BTC Address.")
        exists = self.exists()
        if exists and registering:
            raise LookupError("Address Already Is Registered.")
        elif not exists and not registering:
            raise LookupError("Address Not Registered.")

    def register(self, payout_addr=None):
        """Add the farmer to the database."""
        self.payout_addr = payout_addr if payout_addr else self.btc_addr
        self.validate(registering=True)
        db.session.add(self)
        db.session.commit()

    def exists(self):
        """Check to see if this address is already listed."""
        query = db.session.query(Farmer.btc_addr)
        return query.filter(Farmer.btc_addr == self.btc_addr).count() > 0

    def lookup(self):
        """Return the Farmer object for the bitcoin address passed."""
        farmer = Farmer.query.filter_by(btc_addr=self.btc_addr).first()
        if not farmer:
            raise LookupError("Address Not Registered.")
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
        self.ping()  # also serves as a valid ping
        farmer = self.lookup()
        farmer.height = height
        db.session.commit()
        return self.height

    def to_json(self):
        """Object to JSON payload."""
        payload = {
            "btc_addr": self.btc_addr,
            "payout_addr": self.payout_addr,
            "last_seen": (datetime.utcnow() - self.last_seen).seconds,
            "height": self.height
        }
        return json.dumps(payload)
