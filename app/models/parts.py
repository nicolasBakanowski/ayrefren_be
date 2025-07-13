from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)

    work_orders = relationship("WorkOrderPart", back_populates="part")
