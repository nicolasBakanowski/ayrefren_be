"""Add cost column to parts

Revision ID: bbe21fb15527
Revises: db5e0cd2953c
Create Date: 2025-07-14
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "bbe21fb15527"
down_revision: Union[str, Sequence[str], None] = "db5e0cd2953c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("parts")]
    if "cost" not in columns:
        op.add_column(
            "parts",
            sa.Column(
                "cost",
                sa.Numeric(precision=10, scale=2),
                nullable=False,
                server_default="0",
            ),
        )
        op.alter_column("parts", "cost", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("parts")]
    if "cost" in columns:
        op.drop_column("parts", "cost")
