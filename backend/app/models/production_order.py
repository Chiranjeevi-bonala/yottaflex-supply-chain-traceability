from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import CheckConstraint, Date, Numeric, String, DateTime, ForeignKey, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ProductionOrder(Base):
    __tablename__ = "production_orders"

    order_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(20), ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False, index=True)
    planned_qty: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    actual_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 3))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PLANNED")
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product: Mapped["Product"] = relationship("Product", back_populates="production_orders")
    consumptions: Mapped[List["ProductionConsumption"]] = relationship("ProductionConsumption", back_populates="production_order")
    finished_lots: Mapped[List["FinishedLot"]] = relationship("FinishedLot", back_populates="production_order")

    __table_args__ = (
        CheckConstraint("planned_qty > 0", name="po_planned_qty_positive"),
        CheckConstraint("actual_qty IS NULL OR actual_qty >= 0", name="po_actual_qty_non_negative"),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="po_end_after_start"),
        CheckConstraint("status IN ('PLANNED','IN_PROGRESS','COMPLETED','CANCELLED')", name="po_status_valid"),
        Index("ix_production_orders_status", "status"),
        Index("ix_production_orders_dates", "start_date", "end_date"),
    )

    def __repr__(self) -> str:
        return f"<ProductionOrder {self.order_id} [{self.status}]>"

