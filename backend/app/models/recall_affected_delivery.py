from decimal import Decimal
from datetime import datetime
from sqlalchemy import CheckConstraint, Numeric, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class RecallAffectedDelivery(Base):
    __tablename__ = "recall_affected_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recall_id: Mapped[str] = mapped_column(String(20), ForeignKey("recall_cases.recall_id", ondelete="CASCADE"), nullable=False, index=True)
    delivery_id: Mapped[str] = mapped_column(String(20), ForeignKey("deliveries.delivery_id", ondelete="CASCADE"), nullable=False, index=True)
    qty_in_scope: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recall_case: Mapped["RecallCase"] = relationship("RecallCase", back_populates="affected_deliveries")
    delivery: Mapped["Delivery"] = relationship("Delivery", back_populates="recall_affected_records")

    __table_args__ = (
        CheckConstraint("qty_in_scope >= 0", name="scope_qty_deliv_non_negative"),
        UniqueConstraint("recall_id", "delivery_id", name="uq_recall_delivery"),
    )

