"""empty message

Revision ID: 23c0c62383bb
Revises: d1cb862c6066
Create Date: 2016-03-10 14:46:29.674809

"""

# revision identifiers, used by Alembic.
revision = '23c0c62383bb'
down_revision = 'd1cb862c6066'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from pycoin.encoding import a2b_hashed_base58  # NOQA
from binascii import hexlify  # NOQA
from datetime import datetime, timedelta  # NOQA
from sqlalchemy.ext.declarative import declarative_base  # NOQA


Base = declarative_base()
Session = sa.orm.sessionmaker()


class Farmer(Base):
    __tablename__ = 'farmer'
    id = sa.Column(sa.Integer, primary_key=True)
    btc_addr = sa.Column(sa.String(35), unique=True)  # TODO change to node_id
    payout_addr = sa.Column(sa.String(35))
    height = sa.Column(sa.Integer, default=0)
    last_seen = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)
    reg_time = sa.Column(sa.DateTime, default=datetime.utcnow)
    uptime = sa.Column(sa.Interval, default=timedelta(seconds=0))
    bandwidth = sa.Column(sa.Integer, default=0)
    ip = sa.Column(sa.String(40), default="")


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    op.add_column('farmer', sa.Column('nodeid', sa.String(length=40),
                                      nullable=True))
    for farmer in session.query(Farmer):
        nodeid = hexlify(a2b_hashed_base58(farmer.btc_addr)[1:])
        if isinstance(nodeid, bytes):
            nodeid = nodeid.decode("utf-8")
        farmer.nodeid = nodeid
    session.commit()


def downgrade():
    op.drop_column('farmer', 'nodeid')
