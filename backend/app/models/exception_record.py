from datetime import datetime
from typing import Any, Dict
from sqlalchemy import CheckConstraint, String, DateTime, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ExceptionRecord(Base):
    __tablename__ = "exception_records"

    exception_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    issue_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(60), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    detection_status: Mapped[str] = mapped_column(String(15), nullable=False, default="DETECTED")
    impact_description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_decision: Mapped[str] = mapped_column(Text, nullable=False)
    ground_truth_label: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("issue_type IN ('MISSING_INPUT_LOT','DELIVERY_OVERRUN','MISSED_CUSTOMER','INVENTORY_NOT_QUARANTINED')", name="exception_issue_type_valid"),
        CheckConstraint("detection_status IN ('DETECTED','UNDETECTED')", name="exception_detection_status_valid"),
    )

    def __repr__(self) -> str:
        return f"<ExceptionRecord {self.exception_id} [{self.issue_type}] status={self.detection_status}>"

