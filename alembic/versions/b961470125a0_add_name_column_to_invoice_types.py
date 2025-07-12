"""add name column to invoice_types

Revision ID: b961470125a0
Revises: 603cc80f101c
Create Date: 2025-07-12 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'b961470125a0'
down_revision = '603cc80f101c'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column(
        'invoice_types',
        sa.Column('name', sa.String(length=50), nullable=True)  # nullable=True solo mientras lo llenamos
    )

    # Completar los valores según el código
    op.execute("UPDATE invoice_types SET name='Factura A' WHERE code='A'")
    op.execute("UPDATE invoice_types SET name='Factura C' WHERE code='C'")
    op.execute("UPDATE invoice_types SET name='Remito' WHERE code='R'")

    # Hacer que sea NOT NULL después de poblar
    op.alter_column('invoice_types', 'name', nullable=False)

    # Crear constraint UNIQUE explícito
    op.create_unique_constraint('uq_invoice_types_name', 'invoice_types', ['name'])

def downgrade() -> None:
    op.drop_constraint('uq_invoice_types_name', 'invoice_types', type_='unique')
    op.drop_column('invoice_types', 'name')
