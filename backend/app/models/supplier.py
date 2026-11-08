from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, CheckConstraint, Numeric, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    reliability_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    material_lots: Mapped[List["MaterialLot"]] = relationship("MaterialLot", back_populates="supplier")

    __table_args__ = (
        CheckConstraint("category IN ('CHEMICAL','PACKAGING','RAW_FOOD','INGREDIENT','ADDITIVE')", name="supplier_category_valid"),
        CheckConstraint("reliability_score IS NULL OR (reliability_score >= 0 AND reliability_score <= 1)", name="supplier_reliability_range"),
    )

    def __repr__(self) -> str:
        return f"<Supplier {self.supplier_id}: {self.name}>"

