from decimal import Decimal
from datetime import datetime
from typing import Optional
from sqlalchemy import CheckConstraint, Numeric, String, DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class LotGenealogy(Base):
    __tablename__ = "lot_genealogy"

    genealogy_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    finished_lot_id: Mapped[str] = mapped_column(String(30), ForeignKey("finished_lots.lot_id", ondelete="CASCADE"), nullable=False, index=True)
    material_lot_id_ref: Mapped[str] = mapped_column(String(60), nullable=False)
    material_lot_id: Mapped[Optional[str]] = mapped_column(String(60), ForeignKey("material_lots.lot_id", ondelete="SET NULL"), nullable=True, index=True)
    qty_contributed: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    finished_lot: Mapped["FinishedLot"] = relationship("FinishedLot", back_populates="genealogy_records")
    material_lot: Mapped[Optional["MaterialLot"]] = relationship("MaterialLot", back_populates="genealogy_records")

    __table_args__ = (
        CheckConstraint("qty_contributed > 0", name="genealogy_qty_positive"),
        UniqueConstraint("finished_lot_id", "material_lot_id_ref", name="uq_genealogy_finlot_rawref"),
        Index("ix_lot_genealogy_finished_lot", "finished_lot_id"),
        Index("ix_lot_genealogy_material_lot", "material_lot_id"),
    )

    def __repr__(self) -> str:
        return f"<LotGenealogy finished={self.finished_lot_id} raw_ref={self.material_lot_id_ref}>"

