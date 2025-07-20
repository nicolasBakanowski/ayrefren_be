
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ExpenseType(Base):
    __tablename__ = "expense_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    expenses = relationship("Expense", back_populates="expense_type")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255))
    expense_type_id = Column(
        Integer,
        ForeignKey("expense_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    expense_type = relationship("ExpenseType", back_populates="expenses")
