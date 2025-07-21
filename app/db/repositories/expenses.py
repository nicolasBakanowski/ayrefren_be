from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.expense import Expense, ExpenseType
from app.schemas.expenses import ExpenseCreate


class ExpensesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_types(self) -> list[ExpenseType]:
        result = await self.db.execute(select(ExpenseType))
        return result.scalars().all()

    async def create_expense(self, data: ExpenseCreate) -> Expense:
        expense = Expense(**data.model_dump())
        self.db.add(expense)
        await self.db.commit()
        await self.db.refresh(expense)
        return await self.get_expense(expense.id)

    async def get_expense(self, expense_id: int) -> Expense | None:
        result = await self.db.execute(
            select(Expense)
            .options(selectinload(Expense.expense_type))
            .where(Expense.id == expense_id)
        )
        return result.scalar_one_or_none()

    async def list_expenses(self) -> list[Expense]:
        result = await self.db.execute(
            select(Expense).options(selectinload(Expense.expense_type))
        )
        return result.scalars().all()
