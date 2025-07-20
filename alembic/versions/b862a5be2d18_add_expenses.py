"""add expenses tables

Revision ID: b862a5be2d18
Revises: a7ddd162d893
Create Date: 2025-07-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b862a5be2d18'
down_revision: Union[str, Sequence[str], None] = 'a7ddd162d893'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'expense_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('expense_type_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['expense_type_id'], ['expense_types.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    expense_types = [
        'Sueldos',
        'Alquiler',
        'Luz',
        'Gas',
        'Agua',
        'Internet',
        'Impuestos',
        'Mantenimiento',
    ]
    op.bulk_insert(
        sa.table(
            'expense_types',
            sa.column('name', sa.String),
        ),
        [{'name': n} for n in expense_types],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('expenses')
    op.drop_table('expense_types')
