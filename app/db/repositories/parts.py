from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.parts import Part
from app.schemas.parts import PartCreate, PartUpdate


class PartsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, part_id: int) -> Part | None:
        result = await self.db.execute(
            select(Part).where(Part.id == part_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Part]:
        result = await self.db.execute(select(Part))
        return result.scalars().all()

    async def create(self, data: PartCreate) -> Part:
        part = Part(**data.model_dump())
        self.db.add(part)
        await self.db.commit()
        await self.db.refresh(part)
        return part

    async def update(self, part: Part, data: PartUpdate) -> Part:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(part, key, value)
        await self.db.commit()
        await self.db.refresh(part)
        return part

    async def delete(self, part: Part) -> None:
        await self.db.delete(part)
        await self.db.commit()
