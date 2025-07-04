from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_or_404(db: AsyncSession, model, obj_id: int, name: str = "Recurso"):
    result = await db.execute(select(model).where(model.id == obj_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{name} con ID {obj_id} no existe")
    return obj


async def exists_or_404(db: AsyncSession, model, obj_id: int):
    result = await db.execute(
        select(func.count()).select_from(model).where(model.id == obj_id)
    )
    count = result.scalar_one()
    if count == 0:
        raise HTTPException(
            status_code=404, detail=f"{model.__name__} con id {obj_id} no existe"
        )
    return count > 0
