"""add name column to invoice_types

Revision ID: b961470125a0
Revises: 603cc80f101c
Create Date: 2025-07-12 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b961470125a0'
down_revision: Union[str, Sequence[str], None] = '603cc80f101c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('invoice_types', sa.Column('name', sa.String(length=50), unique=True))
    op.execute(
        "UPDATE invoice_types SET name='Factura A' WHERE code='A'"
    )
    op.execute(
        "UPDATE invoice_types SET name='Factura C' WHERE code='C'"
    )
    op.execute(
        "UPDATE invoice_types SET name='Remito' WHERE code='R'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('invoice_types', 'name')
