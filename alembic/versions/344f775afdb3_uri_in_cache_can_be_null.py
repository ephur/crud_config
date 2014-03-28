"""URI in cache CAN be null

Revision ID: 344f775afdb3
Revises: 38159f231192
Create Date: 2014-03-28 10:29:33.087109

"""

# revision identifiers, used by Alembic.
revision = '344f775afdb3'
down_revision = '38159f231192'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.alter_column('cachereference', 'uri',
               existing_type=mysql.TEXT(),
               nullable=True)


def downgrade():
    op.alter_column('cachereference', 'uri',
               existing_type=mysql.TEXT(),
               nullable=False)
