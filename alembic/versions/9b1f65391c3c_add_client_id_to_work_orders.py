"""add client id to work orders

Revision ID: 9b1f65391c3c
Revises: 603cc80f101c
Create Date: 2025-07-08 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9b1f65391c3c'
down_revision: Union[str, Sequence[str], None] = '603cc80f101c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('work_orders', sa.Column('client_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'work_orders', 'clients', ['client_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'work_orders', type_='foreignkey')
    op.drop_column('work_orders', 'client_id')
