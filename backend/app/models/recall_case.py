from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from sqlalchemy import CheckConstraint, Numeric, String, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class RecallCase(Base):
    __tablename__ = "recall_cases"

    recall_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    trigger_type: Mapped[str] = mapped_column(String(15), nullable=False)
    trigger_lot_id: Mapped[str] = mapped_column(String(60), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False, default="CLASS_II")
    initiated_by: Mapped[str] = mapped_column(String(100), nullable=False, default="System Quality Officer", server_default="System Quality Officer")
    initiated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="OPEN")
    total_qty_affected: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 3))
    total_qty_recovered: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    recall_actions: Mapped[List["RecallAction"]] = relationship("RecallAction", back_populates="recall_case")
    affected_finished_lots: Mapped[List["RecallAffectedFinishedLot"]] = relationship("RecallAffectedFinishedLot", back_populates="recall_case")
    affected_deliveries: Mapped[List["RecallAffectedDelivery"]] = relationship("RecallAffectedDelivery", back_populates="recall_case")

    __table_args__ = (
        CheckConstraint("trigger_type IN ('RAW_LOT','FINISHED_LOT')", name="recall_trigger_type_valid"),
        CheckConstraint("severity IN ('CLASS_I','CLASS_II','CLASS_III')", name="recall_severity_valid"),
        CheckConstraint("status IN ('OPEN','IN_PROGRESS','CLOSED')", name="recall_status_valid"),
        CheckConstraint("total_qty_recovered >= 0", name="recall_qty_recovered_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<RecallCase {self.recall_id} [{self.status}] trigger={self.trigger_lot_id}>"

