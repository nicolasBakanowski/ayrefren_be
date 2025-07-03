import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class ClientType(str, enum.Enum):
    persona = "persona"
    empresa = "empresa"


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ClientType), nullable=False)
    name = Column(String(100), nullable=False)
    document_number = Column(String(30))
    phone = Column(String(30))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
