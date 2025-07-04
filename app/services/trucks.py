from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.trucks import TrucksRepository
from app.models.trucks import Truck
from app.schemas.trucks import TruckCreate, TruckUpdate


class TrucksService:
    def __init__(self, db: AsyncSession):
        self.repo = TrucksRepository(db)

    async def get_truck(self, truck_id: int) -> Truck:
        truck = await self.repo.get_by_id(truck_id)
        if not truck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found"
            )
        return truck

    async def create_truck(self, truck_create: TruckCreate) -> Truck:
        return await self.repo.create(truck_create)

    async def update_truck(self, truck_id: int, truck_update: TruckUpdate) -> Truck:
        truck = await self.repo.get_by_id(truck_id)
        if not truck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found"
            )
        return await self.repo.update(truck, truck_update)

    async def delete_truck(self, truck_id: int) -> None:
        truck = await self.repo.get_by_id(truck_id)
        if not truck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found"
            )
        await self.repo.delete(truck)

    async def list_trucks(
        self,
        client_id: int = None,
        license_plate: str = None,
        brand: str = None,
        model: int = None,
        year: int = None,
    ) -> List[Truck]:
        trucks = await self.repo.list_all(
            client_id=client_id,
            license_plate=license_plate,
            brand=brand,
            model=model,
            year=year,
        )
        if not trucks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No trucks found"
            )
        return trucks
