from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validators import exists_or_404
from app.db.repositories.expenses import ExpensesRepository
from app.models.expense import Expense, ExpenseType
from app.schemas.expenses import ExpenseCreate


class ExpensesService:
    def __init__(self, db: AsyncSession):
        self.repo = ExpensesRepository(db)

    async def get_expense_types(self) -> list[ExpenseType]:
        return await self.repo.list_types()

    async def create_expense(self, expense_data: ExpenseCreate) -> Expense:
        if expense_data.expense_type_id is not None:
            await exists_or_404(self.repo.db, ExpenseType, expense_data.expense_type_id)
        return await self.repo.create_expense(expense_data)

    async def list_expenses(self) -> list[Expense]:
        return await self.repo.list_expenses()
