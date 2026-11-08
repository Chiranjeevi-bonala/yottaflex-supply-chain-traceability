from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import CheckConstraint, Date, Numeric, String, DateTime, ForeignKey, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Delivery(Base):
    __tablename__ = "deliveries"

    delivery_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    shipment_id: Mapped[str] = mapped_column(String(20), ForeignKey("shipments.shipment_id", ondelete="RESTRICT"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(20), ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False, index=True)
    qty_delivered: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DELIVERED")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="deliveries")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="deliveries")
    recall_affected_records: Mapped[List["RecallAffectedDelivery"]] = relationship("RecallAffectedDelivery", back_populates="delivery")

    __table_args__ = (
        CheckConstraint("qty_delivered > 0", name="delivery_qty_positive"),
        CheckConstraint("status IN ('DELIVERED','RETURNED','QUARANTINED')", name="delivery_status_valid"),
        Index("ix_deliveries_customer_date", "customer_id", "delivery_date"),
    )

    def __repr__(self) -> str:
        return f"<Delivery {self.delivery_id} [{self.status}] qty={self.qty_delivered}>"

