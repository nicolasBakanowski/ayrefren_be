"""migraciones

Revision ID: 115029a09549
Revises: b862a5be2d18
Create Date: 2025-07-23 18:24:57.378278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '115029a09549'
down_revision: Union[str, Sequence[str], None] = 'b862a5be2d18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bank_checks', sa.Column('exchange_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bank_checks', 'exchange_date')
    # ### end Alembic commands ###
