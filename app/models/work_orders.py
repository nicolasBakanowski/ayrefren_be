from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class WorkOrderStatus(Base):
    __tablename__ = "work_order_statuses"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status_id = Column(Integer, ForeignKey("work_order_statuses.id"))
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    fast_phone = Column(Text, nullable=True)

    status = relationship("WorkOrderStatus")
    truck = relationship("Truck")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    mechanics = relationship("WorkOrderMechanic", back_populates="work_order")
    tasks = relationship("WorkOrderTask", back_populates="work_order")
    parts = relationship("WorkOrderPart", back_populates="work_order")
