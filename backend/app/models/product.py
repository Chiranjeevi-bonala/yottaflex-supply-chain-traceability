from datetime import datetime
from typing import List
from sqlalchemy import Boolean, CheckConstraint, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    uom: Mapped[str] = mapped_column(String(10), nullable=False)
    shelf_life_days: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    bom_items: Mapped[List["BOM"]] = relationship("BOM", back_populates="product")
    production_orders: Mapped[List["ProductionOrder"]] = relationship("ProductionOrder", back_populates="product")
    finished_lots: Mapped[List["FinishedLot"]] = relationship("FinishedLot", back_populates="product")

    __table_args__ = (
        CheckConstraint("shelf_life_days > 0", name="product_shelf_life_positive"),
        CheckConstraint("uom IN ('KG','UNIT','LITER','G','MT','L')", name="product_uom_valid"),
    )

    def __repr__(self) -> str:
        return f"<Product {self.product_id}: {self.sku}>"

