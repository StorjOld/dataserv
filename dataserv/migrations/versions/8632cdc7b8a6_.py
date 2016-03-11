"""empty message

Revision ID: 8632cdc7b8a6
Revises: 510b23c2ceef
Create Date: 2016-03-11 18:53:37.326967

"""

# revision identifiers, used by Alembic.
revision = '8632cdc7b8a6'
down_revision = '510b23c2ceef'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA
from pycoin.encoding import a2b_hashed_base58  # NOQA
from binascii import hexlify  # NOQA
from datetime import datetime, timedelta  # NOQA
from sqlalchemy.ext.declarative import declarative_base  # NOQA


Base = declarative_base()
Session = sa.orm.sessionmaker()


class Audit(Base):
    __tablename__ = 'audit'
    id = sa.Column(sa.Integer, primary_key=True)
    btc_addr = sa.Column(sa.String(35))
    block = sa.Column(sa.Integer, index=True)
    submit_time = sa.Column(sa.DateTime, default=datetime.utcnow)
    response = sa.Column(sa.String(60))


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    op.add_column('audit', sa.Column('nodeid', sa.String(length=40),
                                     nullable=True))
    for audit in session.query(Audit):
        nodeid = hexlify(a2b_hashed_base58(audit.btc_addr)[1:])
        if isinstance(nodeid, bytes):
            nodeid = nodeid.decode("utf-8")
        audit.nodeid = nodeid
    session.commit()


def downgrade():
    op.drop_column('audit', 'nodeid')
