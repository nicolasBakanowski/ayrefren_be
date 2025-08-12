"""add paid fields to work_order_tasks

Revision ID: d7e6f63ad0a5
Revises: c45d6741ac72
Create Date: 2025-08-12 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7e6f63ad0a5'
down_revision: Union[str, Sequence[str], None] = 'c45d6741ac72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("work_order_tasks") as batch_op:
        batch_op.add_column(sa.Column("paid", sa.Boolean(), nullable=False, server_default=sa.text("false")))
        batch_op.add_column(sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True))

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute(
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_wot_area_created_paid "
                "ON work_order_tasks (area_id, created_at, paid)"
            )
    else:
        op.create_index(
            "ix_wot_area_created_paid",
            "work_order_tasks",
            ["area_id", "created_at", "paid"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute(
                "DROP INDEX CONCURRENTLY IF EXISTS ix_wot_area_created_paid"
            )
    else:
        op.drop_index(
            "ix_wot_area_created_paid", table_name="work_order_tasks"
        )

    with op.batch_alter_table("work_order_tasks") as batch_op:
        batch_op.drop_column("paid")
        batch_op.drop_column("paid_at")
