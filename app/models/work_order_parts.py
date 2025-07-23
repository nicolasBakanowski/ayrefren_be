from sqlalchemy import Column, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class WorkOrderPart(Base):
    __tablename__ = "work_order_parts"

    id = Column(Integer, primary_key=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    name = Column(Text)
    quantity = Column(Integer, nullable=False)
    increment_per_unit = Column(
        Numeric(10, 2), nullable=False, default=1
    )  # Incremento por unidad
    unit_price = Column(
        Numeric(10, 2), nullable=False
    )  # En el caso de que no tengamos incremento
    subtotal = Column(Numeric(10, 2), nullable=False)

    work_order = relationship("WorkOrder", back_populates="parts")
