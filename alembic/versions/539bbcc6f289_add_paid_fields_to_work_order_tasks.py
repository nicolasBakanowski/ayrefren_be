"""add paid fields to work_order_tasks

Revision ID: 539bbcc6f289
Revises: c45d6741ac72
Create Date: 2025-08-12 04:28:49.277339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '539bbcc6f289'
down_revision: Union[str, Sequence[str], None] = 'c45d6741ac72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "work_order_tasks",
        sa.Column("paid", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "work_order_tasks",
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_work_order_tasks_area_paid_created_at",
        "work_order_tasks",
        ["area_id", "paid", "created_at"],
    )
    op.create_index(
        "ix_work_order_tasks_work_order_id",
        "work_order_tasks",
        ["work_order_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_work_order_tasks_work_order_id", table_name="work_order_tasks")
    op.drop_index("ix_work_order_tasks_area_paid_created_at", table_name="work_order_tasks")
    op.drop_column("work_order_tasks", "paid_at")
    op.drop_column("work_order_tasks", "paid")
