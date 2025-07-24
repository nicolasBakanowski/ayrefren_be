from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.trucks import Truck
from app.schemas.trucks import TruckCreate


class TrucksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, truck_id: int) -> Truck | None:
        result = await self.db.execute(
            select(Truck)
            .options(selectinload(Truck.client))
            .where(Truck.id == truck_id)
        )
        return result.scalars().first()

    async def create(self, truck_data: TruckCreate) -> Truck:
        truck = Truck(**truck_data.model_dump())
        self.db.add(truck)
        await self.db.commit()
        await self.db.refresh(truck)
        return await self.get_by_id(truck.id)

    async def update(self, db: AsyncSession, truck: Truck, update_data: dict) -> Truck:
        for key, value in update_data.items():
            setattr(truck, key, value)
        await db.commit()
        await db.refresh(truck)
        return await self.get_by_id(truck.id)

    async def delete(self, truck: Truck) -> None:
        await self.db.delete(truck)
        await self.db.commit()

    async def list_all(
        self,
        client_id: int = None,
        license_plate: str = None,
        brand: str = None,
        model: int = None,
    ):
        filters = []

        if client_id is not None:
            filters.append(Truck.client_id == client_id)
        if license_plate is not None:
            filters.append(
                Truck.license_plate.ilike(f"%{license_plate}%")
            )  # búsqueda parcial
        if brand is not None:
            filters.append(Truck.brand.ilike(f"%{brand}%"))
        if model is not None:
            filters.append(Truck.model == model)

        query = select(Truck).options(selectinload(Truck.client))
        if filters:
            query = query.where(and_(*filters))

        result = await self.db.execute(query)
        return result.scalars().all()
