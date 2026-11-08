from decimal import Decimal
from datetime import datetime
from typing import Optional
from sqlalchemy import CheckConstraint, Numeric, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class RecallAction(Base):
    __tablename__ = "recall_actions"

    action_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    recall_id: Mapped[str] = mapped_column(String(20), ForeignKey("recall_cases.recall_id", ondelete="CASCADE"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(15), nullable=False)
    target_entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_entity_id: Mapped[str] = mapped_column(String(60), nullable=False)
    qty_affected: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 3))
    qty_actioned: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 3))
    actioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="COMPLETED")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recall_case: Mapped["RecallCase"] = relationship("RecallCase", back_populates="recall_actions")

    __table_args__ = (
        CheckConstraint("action_type IN ('NOTIFY','QUARANTINE','RECOVER')", name="action_type_valid"),
        CheckConstraint("target_entity_type IN ('CUSTOMER','FINISHED_LOT','SHIPMENT','DELIVERY')", name="action_target_type_valid"),
        CheckConstraint("status IN ('PENDING','COMPLETED','FAILED')", name="action_status_valid"),
    )

    def __repr__(self) -> str:
        return f"<RecallAction {self.action_id} [{self.action_type}] target={self.target_entity_id}>"

