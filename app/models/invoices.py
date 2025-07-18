from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class InvoiceStatus(Base):
    __tablename__ = "invoice_statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class InvoiceType(Base):
    __tablename__ = "invoice_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    surcharge = Column(Numeric(5, 2), default=0)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    invoice_type_id = Column(Integer, ForeignKey("invoice_types.id"))
    status_id = Column(Integer, ForeignKey("invoice_statuses.id"))
    labor_total = Column(Numeric(10, 2), nullable=False)
    parts_total = Column(Numeric(10, 2), nullable=False)
    iva = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    paid = Column(Numeric(10, 2), default=0)
    invoice_number = Column(String(30), nullable=True)

    work_order = relationship("WorkOrder")
    client = relationship("Client")
    invoice_type = relationship("InvoiceType")
    status = relationship("InvoiceStatus")
    payments = relationship("Payment", back_populates="invoice")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    method_id = Column(Integer, ForeignKey("payment_methods.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    reference = Column(String(100), nullable=True)
    notes = Column(String(255), nullable=True)

    invoice = relationship("Invoice", back_populates="payments")
    method = relationship("PaymentMethod")
    bank_checks = relationship(
        "BankCheck",
        back_populates="payment",
        cascade="all, delete-orphan",
    )


class BankCheckType(str, Enum):
    PHYSICAL = "physical"
    ELECTRONIC = "electronic"


class BankCheck(Base):
    __tablename__ = "bank_checks"

    id = Column(Integer, primary_key=True)
    bank_name = Column(String(100), nullable=False)
    check_number = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    exchange_date = Column(DateTime, nullable=True)
    type = Column(SqlEnum(BankCheckType), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    payment = relationship("Payment", back_populates="bank_checks")
