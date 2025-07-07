"""seed work order statuses

Revision ID: d9a4d651bf05
Revises: 8969ddfc864e
Create Date: 2025-07-03 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d9a4d651bf05"
down_revision: Union[str, Sequence[str], None] = "8969ddfc864e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert default work order statuses."""
    statuses_table = sa.table(
        "work_order_statuses",
        sa.column("id", sa.Integer),
        sa.column("name", sa.Text),
    )
    op.bulk_insert(
        statuses_table,
        [
            {"id": 1, "name": "Pendiente"},
            {"id": 2, "name": "En progreso"},
            {"id": 3, "name": "Finalizado"},
        ],
    )


def downgrade() -> None:
    """Remove default work order statuses."""
    op.execute(sa.text("DELETE FROM work_order_statuses WHERE id IN (1, 2, 3)"))
