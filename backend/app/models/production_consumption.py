from decimal import Decimal
from datetime import datetime
from sqlalchemy import CheckConstraint, Numeric, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ProductionConsumption(Base):
    __tablename__ = "production_consumptions"

    consumption_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(20), ForeignKey("production_orders.order_id", ondelete="CASCADE"), nullable=False, index=True)
    lot_id: Mapped[str] = mapped_column(String(60), ForeignKey("material_lots.lot_id", ondelete="RESTRICT"), nullable=False, index=True)
    qty_consumed: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    consumed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    production_order: Mapped["ProductionOrder"] = relationship("ProductionOrder", back_populates="consumptions")
    material_lot: Mapped["MaterialLot"] = relationship("MaterialLot", back_populates="consumptions")

    __table_args__ = (
        CheckConstraint("qty_consumed > 0", name="consumption_qty_positive"),
        UniqueConstraint("order_id", "lot_id", name="uq_consumption_order_lot"),
    )

    def __repr__(self) -> str:
        return f"<ProductionConsumption order={self.order_id} lot={self.lot_id} qty={self.qty_consumed}>"

