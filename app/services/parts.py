from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.parts import PartsRepository
from app.models.parts import Part
from app.schemas.parts import PartCreate, PartUpdate


class PartsService:
    def __init__(self, db: AsyncSession):
        self.repo = PartsRepository(db)

    async def list_parts(self) -> list[Part]:
        return await self.repo.list_all()

    async def get_part(self, part_id: int) -> Part:
        part = await self.repo.get_by_id(part_id)
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
            )
        return part

    async def create_part(self, data: PartCreate) -> Part:
        return await self.repo.create(data)

    async def update_part(self, part_id: int, data: PartUpdate) -> Part:
        part = await self.get_part(part_id)
        return await self.repo.update(part, data)

    async def delete_part(self, part_id: int) -> None:
        part = await self.get_part(part_id)
        await self.repo.delete(part)