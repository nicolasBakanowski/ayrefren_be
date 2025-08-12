"""add paid column to work_order_tasks

Revision ID: 431d1d01c921
Revises: c45d6741ac72
Create Date: 2025-08-12 21:10:17.930134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '431d1d01c921'
down_revision: Union[str, Sequence[str], None] = 'c45d6741ac72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "work_order_tasks",
        sa.Column(
            "paid",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("work_order_tasks", "paid")
