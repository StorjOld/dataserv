import json
import hashlib
import storjcore
from sqlalchemy import DateTime
from dataserv.run import db, app
from btctxstore import BtcTxStore
from datetime import datetime, timedelta


from dataserv.config import logging
logger = logging.getLogger(__name__)
is_btc_address = BtcTxStore().validate_address


def sha256(content):
    """Finds the sha256 hash of the content."""
    content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()


class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    btc_addr = db.Column(db.String(35), unique=True)  # TODO change to node_id
    payout_addr = db.Column(db.String(35))
    height = db.Column(db.Integer, default=0)

    last_seen = db.Column(DateTime, index=True, default=datetime.utcnow)
    reg_time = db.Column(DateTime, default=datetime.utcnow)
    uptime = db.Column(db.Interval, default=timedelta(seconds=0))

    bandwidth = db.Column(db.Integer, default=0)
    ip = db.Column(db.String(40), default="")  # TODO save ip

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

    def authenticate(self, headers):
        if app.config["SKIP_AUTHENTICATION"]:
            return True

        if not headers.get("Authorization"):
            raise storjcore.auth.AuthError("Authorization header required!")
        if not headers.get("Date"):
            raise storjcore.auth.AuthError("Date header required!")

        btctxstore = BtcTxStore()
        timeout = self.get_server_authentication_timeout()
        recipient_address = self.get_server_address()
        sender_address = self.btc_addr
        return storjcore.auth.verify_headers(btctxstore, headers, timeout,
                                             sender_address, recipient_address)

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

        return self.reg_time

    def exists(self):
        """Check to see if this address is already listed."""
        return Farmer.query.filter(Farmer.btc_addr ==
                                   self.btc_addr).count() > 0

    def lookup(self):
        """Return the Farmer object for the bitcoin address passed."""
        farmer = Farmer.query.filter_by(btc_addr=self.btc_addr).first()
        if not farmer:
            msg = "Address not registered: {0}".format(self.btc_addr)
            logger.warning(msg)
            raise LookupError(msg)
        return farmer

    def ping(self, before_commit_callback=None, ip=None):
        """
        Keep-alive for the farmer. Validation can take a long time, so
        we just want to know if they are still there.

        """
        ping_time = datetime.utcnow()

        # make sure the farmer is valid
        farmer = self.lookup()
        # find time delta since we last pinged
        delta_ping = ping_time - farmer.last_seen

        # if we are above the time limit, update last seen
        if delta_ping >= timedelta(seconds=app.config["MAX_PING"]):
            farmer.last_seen = ping_time
            # if the farmer has been online in the last ONLINE_TIME seconds
            # then we can update their uptime statistic
            if farmer.uptime is None:
                farmer.uptime = timedelta(seconds=0)
            if delta_ping <= timedelta(minutes=app.config["ONLINE_TIME"]):
                farmer.uptime += delta_ping
            else:
                farmer.uptime += timedelta(
                    minutes=app.config["ONLINE_TIME"])
            # call to the authentication module
            if before_commit_callback:
                before_commit_callback()

            # update the ip while were at it
            if ip is not None:
                farmer.ip = ip

            db.session.commit()

    def audit(self, ip=None):
        """
        Complete a cryptographic audit of files stored on the farmer. If
        the farmer completes an audit we also update when we last saw them.

        """
        self.ping(ip=ip)

    def set_height(self, height, ip=None):
        """Set the farmers advertised height."""
        farmer = self.lookup()
        farmer.height = height
        # better 2 db commits than implementing ping with
        # update calculation again
        self.ping(ip=ip)
        db.session.commit()
        return self.height

    def calculate_uptime(self):
        """Calculate uptime from registration date."""
        farmer = self.lookup()

        # save datetime.utcnow() to avoid a difference
        utcnow = datetime.utcnow()
        # time delta from registration and ping
        delta_reg = utcnow - farmer.reg_time
        delta_ping = utcnow - farmer.last_seen

        # in case registration happened a short bit ago
        if delta_reg < timedelta(seconds=1):
            return 100.0

        if delta_ping <= timedelta(minutes=app.config["ONLINE_TIME"]):
            if farmer.uptime is None:
                farmer_uptime = delta_ping
            else:
                farmer_uptime = farmer.uptime + delta_ping
        else:
            farmer_uptime = farmer.uptime + timedelta(
                minutes=app.config["ONLINE_TIME"])
        uptime = round(farmer_uptime.total_seconds() /
                       delta_reg.total_seconds(), 3)
        # clip if we completed the audit recently (which sends us over 100%)
        uptime *= 100  # covert from decimal to percentage

        return round(uptime, 3)

    def to_json(self):
        """Object to JSON payload."""
        epoch = datetime.utcfromtimestamp(0)
        payload = {
            "btc_addr": self.btc_addr,
            "payout_addr": self.payout_addr,
            "last_seen": (datetime.utcnow() - self.last_seen).seconds,
            "height": self.height,
            "uptime": self.calculate_uptime(),
            "reg_time": int((self.reg_time - epoch).total_seconds()),
            "bandwidth": self.bandwidth,
            "ip": self.ip,
        }
        return json.dumps(payload)
