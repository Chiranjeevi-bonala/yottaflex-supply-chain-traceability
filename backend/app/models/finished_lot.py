from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import CheckConstraint, Date, Numeric, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class FinishedLot(Base):
    __tablename__ = "finished_lots"

    lot_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(20), ForeignKey("production_orders.order_id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(20), ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity_produced: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    qty_remaining: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    production_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(25), nullable=False, default="IN_WAREHOUSE")
    storage_location: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    production_order: Mapped["ProductionOrder"] = relationship("ProductionOrder", back_populates="finished_lots")
    product: Mapped["Product"] = relationship("Product", back_populates="finished_lots")
    genealogy_records: Mapped[List["LotGenealogy"]] = relationship("LotGenealogy", back_populates="finished_lot")
    shipments: Mapped[List["Shipment"]] = relationship("Shipment", back_populates="finished_lot")
    recall_affected_records: Mapped[List["RecallAffectedFinishedLot"]] = relationship("RecallAffectedFinishedLot", back_populates="finished_lot")

    __table_args__ = (
        CheckConstraint("quantity_produced > 0", name="finlot_qty_produced_positive"),
        CheckConstraint("qty_remaining >= 0", name="finlot_qty_remaining_non_negative"),
        CheckConstraint("qty_remaining <= quantity_produced", name="finlot_qty_remaining_lte_produced"),
        CheckConstraint("expiry_date > production_date", name="finlot_expiry_after_production"),
        CheckConstraint("status IN ('PRODUCED','IN_WAREHOUSE','SHIPPED','PARTIALLY_SHIPPED','QUARANTINED','RECALLED','DISPOSED')", name="finlot_status_valid"),
        Index("ix_finished_lots_status", "status"),
        Index("ix_finished_lots_product_date", "product_id", "production_date"),
    )

    def __repr__(self) -> str:
        return f"<FinishedLot {self.lot_id} [{self.status}] produced={self.quantity_produced}>"

