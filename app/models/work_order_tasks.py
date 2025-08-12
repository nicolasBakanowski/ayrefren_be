from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class WorkOrderTask(Base):
    __tablename__ = "work_order_tasks"

    id = Column(Integer, primary_key=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=False)
    area_id = Column(Integer, ForeignKey("work_areas.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    external = Column(Boolean, default=False)
    paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    work_order = relationship("WorkOrder", back_populates="tasks")
    user = relationship("User")
    area = relationship("WorkArea")
