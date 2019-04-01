"""reservation table

Revision ID: 44567dfc2c69
Revises: None
Create Date: 2019-04-01 10:55:54.844451

"""

# revision identifiers, used by Alembic.
revision = '44567dfc2c69'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
    Create table reservation
    """
    op.create_table(
        'reservation',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('event_id', sa.Integer, nullable=False),
        sa.Column('create_date', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('update_date', sa.DateTime, nullable=True)
    )


def downgrade():
    """
    Delete table
    """
    op.drop_table('reservation')
