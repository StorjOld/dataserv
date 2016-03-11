"""empty message

Revision ID: ae92fec5e57d
Revises: 1948f2a28c00
Create Date: 2016-03-11 19:44:28.041788

"""


# revision identifiers, used by Alembic.
revision = 'ae92fec5e57d'
down_revision = '1948f2a28c00'


from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA


def upgrade():
    op.add_column('farmer', sa.Column('bandwidth_download',
                                      sa.Integer(), nullable=True))
    op.add_column('farmer', sa.Column('bandwidth_upload',
                                      sa.Integer(), nullable=True))
    with op.batch_alter_table('farmer') as batch_op:
        batch_op.drop_column('bandwidth')


def downgrade():
    op.add_column('farmer', sa.Column('bandwidth', sa.INTEGER(), nullable=True))
    with op.batch_alter_table('farmer') as batch_op:
        batch_op.drop_column('bandwidth_upload')
        batch_op.drop_column('bandwidth_download')
