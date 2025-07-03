from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.trucks import Truck
from app.schemas.trucks import TruckCreate


class TrucksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, truck_id: int) -> Truck | None:
        result = await self.db.execute(select(Truck).where(Truck.id == truck_id))
        return result.scalars().first()

    async def create(self, truck_data: TruckCreate) -> Truck:
        truck = Truck(**truck_data.model_dump())
        self.db.add(truck)
        await self.db.commit()
        await self.db.refresh(truck)
        return truck

    async def update(self, db: AsyncSession, truck: Truck, update_data: dict) -> Truck:
        for key, value in update_data.items():
            setattr(truck, key, value)
        await db.commit()
        await db.refresh(truck)
        return truck

    async def delete(self, truck: Truck) -> None:
        await self.db.delete(truck)
        await self.db.commit()

    async def list_all(self):
        result = await self.db.execute(select(Truck))
        return result.scalars().all()
