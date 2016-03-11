"""empty message

Revision ID: 1948f2a28c00
Revises: 8632cdc7b8a6
Create Date: 2016-03-11 19:03:49.372896

"""

# revision identifiers, used by Alembic.
revision = '1948f2a28c00'
down_revision = '8632cdc7b8a6'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA


def upgrade():
    with op.batch_alter_table('audit') as batch_op:
        batch_op.drop_column('btc_addr')


def downgrade():
    op.add_column('audit', sa.Column('btc_addr', sa.VARCHAR(length=35),
                                     nullable=True))
