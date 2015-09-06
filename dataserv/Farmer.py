import json
import hashlib
import logging
from email.utils import parsedate_tz
from email.utils import mktime_tz
from dataserv.run import db, app
from datetime import datetime
from datetime import timedelta
from sqlalchemy import DateTime
from btctxstore import BtcTxStore


from dataserv.config import logging
logger = logging.getLogger(__name__)
is_btc_address = BtcTxStore().validate_address


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
            msg = "Invalid BTC Address: {0}".format(btc_addr)
            logger.warning(msg)
            raise ValueError(msg)
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
            msg = "Header authorization required!"
            logger.warning(msg)
            raise AuthError(msg)
        if not header_date:
            msg = "Header date required!"
            logger.warning(msg)
            raise AuthError(msg)

        # verify date
        serverdate = datetime.now()
        clientdate = datetime.fromtimestamp(mktime_tz(parsedate_tz(header_date)))
        timeout = self.get_server_authentication_timeout()
        if serverdate >= clientdate:
            delta = serverdate - clientdate
        else:
            delta = clientdate - serverdate
        if delta.seconds >= timeout or delta.days > 0:
            msg = "Header date to old! {0} >= {1}".format(delta, timeout)
            logger.warning(msg)
            raise AuthError(msg)

        # verify signature
        message = self.get_server_address() + " " + header_date
        if not BtcTxStore().verify_signature_unicode(self.btc_addr,
                                                     header_authorization,
                                                     message):
            msg = "Invalid header_authorization!"
            logger.warning(msg)
            raise AuthError(msg)
        return True

    def validate(self, registering=False):
        """Make sure this farmer fits the rules for this node."""
        if not is_btc_address(self.payout_addr):
            msg = "Invalid BTC Address: {0}".format(self.payout_addr)
            logger.warning(msg)
            raise ValueError(msg)
        exists = self.exists()
        if exists and registering:
            msg = "Address already registered: {0}".format(self.payout_addr)
            logger.warning(msg)
            raise LookupError(msg)

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
            msg = "Address not registered: {0}".format(self.btc_addr)
            logger.warning(msg)
            raise LookupError(msg)
        return farmer

    def ping(self):
        """
        Keep-alive for the farmer. Validation can take a long time, so
        we just want to know if they are still there.

        """
        farmer = self.lookup()
        delta = datetime.utcnow() - farmer.last_seen
        time_limit = delta.seconds >= app.config["MAX_PING"]

        if time_limit:
            farmer.last_seen = datetime.utcnow()
            db.session.commit()
        # else just ignore

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
