from decimal import Decimal
from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, Numeric, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class BOM(Base):
    __tablename__ = "bom_items"

    bom_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(20), ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False, index=True)
    material_type: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="KG")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product: Mapped["Product"] = relationship("Product", back_populates="bom_items")

    __table_args__ = (
        CheckConstraint("quantity_per_unit > 0", name="bom_qty_per_unit_positive"),
        UniqueConstraint("product_id", "material_type", name="uq_bom_product_material"),
    )

    def __repr__(self) -> str:
        return f"<BOM {self.bom_id}: {self.material_type} for {self.product_id}>"

