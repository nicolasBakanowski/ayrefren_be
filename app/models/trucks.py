from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Truck(Base):
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False)
    brand = Column(String(50))
    model = Column(String(50))
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    client = relationship("Client")
