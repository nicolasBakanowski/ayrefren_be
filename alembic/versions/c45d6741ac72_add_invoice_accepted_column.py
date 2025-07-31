"""add invoice accepted column

Revision ID: c45d6741ac72
Revises: b32dd8c9c367
Create Date: 2025-07-31 01:40:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c45d6741ac72'
down_revision: Union[str, Sequence[str], None] = 'b32dd8c9c367'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "invoices",
        sa.Column(
            "accepted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('invoices', 'accepted')
