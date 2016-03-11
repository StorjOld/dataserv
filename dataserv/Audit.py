from dataserv.run import db
from datetime import datetime
from sqlalchemy import DateTime
from btctxstore import BtcTxStore
from dataserv.Farmer import Farmer, address2nodeid, NODEID_PATTERN
from dataserv.Validator import is_sha256
from dataserv.config import logging
import re


logger = logging.getLogger(__name__)
is_btc_address = BtcTxStore().validate_address


class Audit(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nodeid = db.Column(db.String(40))
    block = db.Column(db.Integer, index=True)
    submit_time = db.Column(DateTime, default=datetime.utcnow)
    response = db.Column(db.String(60))

    def __init__(self, nodeid, block, response=None):
        if not re.match(NODEID_PATTERN, nodeid):
            msg = "Invalid nodeid: {0}".format(nodeid)
            logger.warning(msg)
            raise ValueError(msg)
        if not Farmer(nodeid).exists():
            msg = "Farmer Not Found: {0}".format(nodeid)
            logger.warning(msg)
            raise LookupError(msg)
        if response is not None and not is_sha256(response):
            msg = "Invalid Response: {0}".format(response)
            logger.warning(msg)
            raise TypeError(msg)

        self.nodeid = nodeid
        self.block = block
        self.response = response

    def __eq__(self, other):
        return (self.nodeid == other.nodeid and self.block == other.block
                and self.response == other.response)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def exists(self):
        """Check to see if this address is already listed."""
        response = Audit.query.filter(Audit.nodeid == self.nodeid,
                                      Audit.block == self.block).count() > 0
        return response

    def lookup(self):
        """Return the Farmer object for the bitcoin address passed."""
        audit = Audit.query.filter_by(nodeid=self.nodeid,
                                      block=self.block).first()
        if not audit:
            msg = "Block {0} Audit Missing: {1}".format(self.block, self.nodeid)
            logger.warning(msg)
            raise LookupError(msg)

        return audit
