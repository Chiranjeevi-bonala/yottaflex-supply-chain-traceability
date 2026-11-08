from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import Boolean, CheckConstraint, Date, Numeric, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class MaterialLot(Base):
    __tablename__ = "material_lots"

    lot_id: Mapped[str] = mapped_column(String(60), primary_key=True)
    supplier_id: Mapped[str] = mapped_column(String(20), ForeignKey("suppliers.supplier_id", ondelete="RESTRICT"), nullable=False, index=True)
    material_type: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    qty_remaining_kg: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False, default="KG")
    receipt_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(25), nullable=False, default="RECEIVED")
    storage_location: Mapped[Optional[str]] = mapped_column(String(100))
    is_contaminated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="material_lots")
    consumptions: Mapped[List["ProductionConsumption"]] = relationship("ProductionConsumption", back_populates="material_lot")
    genealogy_records: Mapped[List["LotGenealogy"]] = relationship("LotGenealogy", back_populates="material_lot")

    __table_args__ = (
        CheckConstraint("quantity_kg > 0", name="matlot_qty_positive"),
        CheckConstraint("qty_remaining_kg >= 0", name="matlot_remaining_non_negative"),
        CheckConstraint("qty_remaining_kg <= quantity_kg", name="matlot_remaining_lte_original"),
        CheckConstraint("expiry_date > receipt_date", name="matlot_expiry_after_receipt"),
        CheckConstraint("status IN ('RECEIVED','IN_STOCK','PARTIALLY_CONSUMED','CONSUMED','QUARANTINED','DISPOSED')", name="matlot_status_valid"),
        Index("ix_material_lots_supplier_type", "supplier_id", "material_type"),
        Index("ix_material_lots_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<MaterialLot {self.lot_id} [{self.status}]>"

