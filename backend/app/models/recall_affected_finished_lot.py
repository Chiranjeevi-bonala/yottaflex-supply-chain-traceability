from decimal import Decimal
from datetime import datetime
from sqlalchemy import CheckConstraint, Numeric, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class RecallAffectedFinishedLot(Base):
    __tablename__ = "recall_affected_finished_lots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recall_id: Mapped[str] = mapped_column(String(20), ForeignKey("recall_cases.recall_id", ondelete="CASCADE"), nullable=False, index=True)
    finished_lot_id: Mapped[str] = mapped_column(String(30), ForeignKey("finished_lots.lot_id", ondelete="CASCADE"), nullable=False, index=True)
    qty_in_scope: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recall_case: Mapped["RecallCase"] = relationship("RecallCase", back_populates="affected_finished_lots")
    finished_lot: Mapped["FinishedLot"] = relationship("FinishedLot", back_populates="recall_affected_records")

    __table_args__ = (
        CheckConstraint("qty_in_scope >= 0", name="scope_qty_finlot_non_negative"),
        UniqueConstraint("recall_id", "finished_lot_id", name="uq_recall_finlot"),
    )

