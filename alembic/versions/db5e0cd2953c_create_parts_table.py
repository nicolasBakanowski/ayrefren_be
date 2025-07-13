"""Create parts table

Revision ID: db5e0cd2953c
Revises: b961470125a0
Create Date: 2025-07-12 21:46:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'db5e0cd2953c'
down_revision: Union[str, Sequence[str], None] = 'b961470125a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'parts' not in inspector.get_table_names():
        op.create_table(
            'parts',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.String(length=255), nullable=True),
            sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'parts' in inspector.get_table_names():
        op.drop_table('parts')
