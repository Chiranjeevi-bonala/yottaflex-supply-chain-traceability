from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import CheckConstraint, Date, Numeric, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    finished_lot_id: Mapped[str] = mapped_column(String(30), ForeignKey("finished_lots.lot_id", ondelete="RESTRICT"), nullable=False, index=True)
    carrier: Mapped[str] = mapped_column(String(100), nullable=False)
    ship_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_delivery_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="CREATED")
    qty_shipped: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    destination_region: Mapped[Optional[str]] = mapped_column(String(100))
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    finished_lot: Mapped["FinishedLot"] = relationship("FinishedLot", back_populates="shipments")
    deliveries: Mapped[List["Delivery"]] = relationship("Delivery", back_populates="shipment")

    __table_args__ = (
        CheckConstraint("qty_shipped > 0", name="shipment_qty_positive"),
        CheckConstraint("expected_delivery_date >= ship_date", name="shipment_expected_after_ship"),
        CheckConstraint("actual_delivery_date IS NULL OR actual_delivery_date >= ship_date", name="shipment_actual_after_ship"),
        CheckConstraint("status IN ('CREATED','IN_TRANSIT','DELIVERED','RECALLED','QUARANTINED')", name="shipment_status_valid"),
        Index("ix_shipments_status", "status"),
        Index("ix_shipments_ship_date", "ship_date"),
    )

    def __repr__(self) -> str:
        return f"<Shipment {self.shipment_id} [{self.status}] qty={self.qty_shipped}>"

