from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class WorkArea(Base):
    __tablename__ = "work_areas"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    mechanics = relationship("WorkOrderMechanic", back_populates="area")


class WorkOrderMechanic(Base):
    __tablename__ = "work_order_mechanics"

    id = Column(Integer, primary_key=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    area_id = Column(Integer, ForeignKey("work_areas.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    work_order = relationship("WorkOrder", back_populates="mechanics")
    mechanic = relationship("User")
    area = relationship("WorkArea", back_populates="mechanics")
