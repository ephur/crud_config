"""add column for read/write access

Revision ID: 2fc8c5836a0b
Revises: None
Create Date: 2014-03-06 11:11:51.855743

"""

# revision identifiers, used by Alembic.
revision = '2fc8c5836a0b'
down_revision = None

from alembic import op
from sqlalchemy import Column, BOOLEAN, ForeignKey


def upgrade():
    op.add_column('apikeys',Column('write', BOOLEAN, default=False, server_default='0'))

def downgrade():
    op.drop_column('apikeys','write')
