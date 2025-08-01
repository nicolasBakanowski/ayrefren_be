"""Add BankCheckType enum

Revision ID: 319d8bbaa5f9
Revises: 8969ddfc864e
Create Date: 2025-07-07 18:04:14.754069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '319d8bbaa5f9'
down_revision: Union[str, Sequence[str], None] = '8969ddfc864e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bank_checks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bank_name', sa.String(length=100), nullable=False),
    sa.Column('check_number', sa.String(length=50), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('issued_at', sa.DateTime(), nullable=True),
    sa.Column('type', sa.Enum('PHYSICAL', 'ELECTRONIC', name='bankchecktype'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bank_checks')
    # ### end Alembic commands ###
