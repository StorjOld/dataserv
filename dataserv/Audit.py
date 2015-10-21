from datetime import datetime
from sqlalchemy import DateTime
from dataserv.run import db, app
from btctxstore import BtcTxStore
from dataserv.Farmer import Farmer
from dataserv.Validator import is_sha256

from dataserv.config import logging
logger = logging.getLogger(__name__)
is_btc_address = BtcTxStore().validate_address


class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    btc_addr = db.Column(db.String(35))
    block = db.Column(db.Integer, index=True)
    submit_time = db.Column(DateTime, default=datetime.utcnow)

    response = db.Column(db.String(60))

    def __init__(self, btc_addr, block, response=None):
        if not is_btc_address(btc_addr):
            msg = "Invalid BTC Address: {0}".format(btc_addr)
            logger.warning(msg)
            raise ValueError(msg)
        if not Farmer(btc_addr).exists():
            msg = "Farmer Not Found: {0}".format(btc_addr)
            logger.warning(msg)
            raise LookupError(msg)
        if self.exists():
            msg = "Audit already submitted for that block."
            logger.warning(msg)
            raise IndexError(msg)
        if not response is None and not is_sha256(response):
            msg = "Invalid Response: {0}".format(response)
            logger.warning(msg)
            raise ValueError(msg)

        self.btc_addr = btc_addr
        self.block = block
        self.response = response

    def save(self):
        db.session.add(self)
        db.session.commit()

    def exists(self):
        """Check to see if this address is already listed."""
        return Audit.query.filter(Audit.btc_addr == self.btc_addr,
                                  Audit.block == self.block).count() > 0

    def lookup(self): 
        """Return the Farmer object for the bitcoin address passed."""
        audit = Audit.query.filter_by(btc_addr=self.btc_addr,
                                      block=self.block).first()
        if not audit:
            msg = "Block {0} Audit Missing: {1}".format(self.block, self.btc_addr)
            logger.warning(msg)
            raise LookupError(msg)

        return audit
