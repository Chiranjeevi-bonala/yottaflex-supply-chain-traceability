from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, CheckConstraint, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    tier: Mapped[str] = mapped_column(String(10), nullable=False, default="STANDARD")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deliveries: Mapped[List["Delivery"]] = relationship("Delivery", back_populates="customer")

    __table_args__ = (
        CheckConstraint("tier IN ('GOLD','SILVER','BRONZE','STANDARD')", name="customer_tier_valid"),
    )

    def __repr__(self) -> str:
        return f"<Customer {self.customer_id}: {self.name}>"

