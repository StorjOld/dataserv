from datetime import  datetime
from sqlalchemy import DateTime
from dataserv.run import db, app
from btctxstore import BtcTxStore

from dataserv.config import logging
logger = logging.getLogger(__name__)
is_btc_address = BtcTxStore().validate_address


class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    btc_addr = db.Column(db.String(35))
    block = db.Column(db.Integer, index=True)
    submit_time = db.Column(DateTime, index=True, default=datetime.utcnow)

    response = db.Column(db.String(60))


def __init__(self, btc_addr, block):
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
        self.block = block
