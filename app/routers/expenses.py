from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.responses import success_response
from app.schemas.expenses import ExpenseCreate, ExpenseOut, ExpenseTypeOut
from app.schemas.response import ResponseSchema
from app.services.expenses import ExpensesService

expenses_router = APIRouter()


@expenses_router.get("/expense-types", response_model=ResponseSchema[list[ExpenseTypeOut]])
async def list_expense_types(db: AsyncSession = Depends(get_db)):
    service = ExpensesService(db)
    data = await service.get_expense_types()
    return success_response(data=data)


@expenses_router.get("/expenses", response_model=ResponseSchema[list[ExpenseOut]])
async def list_expenses(db: AsyncSession = Depends(get_db)):
    service = ExpensesService(db)
    data = await service.list_expenses()
    return success_response(data=data)


@expenses_router.post("/expenses", response_model=ResponseSchema[ExpenseOut])
async def create_expense(expense_in: ExpenseCreate, db: AsyncSession = Depends(get_db)):
    service = ExpensesService(db)
    data = await service.create_expense(expense_in)
    return success_response(data=data)
