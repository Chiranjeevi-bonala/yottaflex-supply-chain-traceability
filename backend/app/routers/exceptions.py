from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.exception_record import ExceptionRecord
from app.schemas.entities import ExceptionRecordResponse
from app.engine.exception_detector import ExceptionDetector

router = APIRouter(prefix="/api/exceptions", tags=["Exceptions & Audit"])

@router.get("", response_model=List[ExceptionRecordResponse])
def list_exception_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    issue_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(ExceptionRecord)
    if issue_type:
        query = query.where(ExceptionRecord.issue_type == issue_type)
    if entity_type:
        query = query.where(ExceptionRecord.entity_type == entity_type)
    query = query.offset(skip).limit(limit)
    records = db.execute(query).scalars().all()
    return records

@router.get("/detected")
def get_detected_exceptions(db: Session = Depends(get_db)):
    """
    Executes automated detection algorithms across live database tables:
      - EC-01: Finished lot references missing input lot
      - EC-02: Delivered quantity exceeds produced quantity
      - EC-03: Recall misses a downstream customer
      - EC-04: Recalled inventory remains available for sale
    """
    return ExceptionDetector.run_all_detectors(db)

@router.get("/audit-report")
def get_audit_report(db: Session = Depends(get_db)):
    results = ExceptionDetector.run_all_detectors(db)
    return {
        "audit_timestamp": "2026-11-08T01:30:00Z",
        "system_status": results["status"],
        "total_anomalies_flagged": results["total_detected_exceptions"],
        "remediation_summary": [
            {
                "category": "MISSING_INPUT_LOT",
                "count": len(results["exceptions_by_category"]["missing_input_lots"]),
                "protocol": "Immediate quarantine of batch; check ERP input lot entry",
            },
            {
                "category": "DELIVERY_OVERRUN",
                "count": len(results["exceptions_by_category"]["delivery_overruns"]),
                "protocol": "Lock shipping manifests; audit physical pallet counts at distribution center",
            },
            {
                "category": "MISSED_CUSTOMER",
                "count": len(results["exceptions_by_category"]["missed_customers"]),
                "protocol": "Emergency dispatch of priority notification to unnotified customer",
            },
            {
                "category": "INVENTORY_NOT_QUARANTINED",
                "count": len(results["exceptions_by_category"]["unquarantined_inventory"]),
                "protocol": "Lock WMS storage bay; apply red physical tag on warehouse bins",
            },
        ],
        "details": results["exceptions_by_category"]
    }

@router.get("/{exception_id}", response_model=ExceptionRecordResponse)
def get_exception_record(exception_id: str, db: Session = Depends(get_db)):
    exc = db.execute(select(ExceptionRecord).where(ExceptionRecord.exception_id == exception_id)).scalar_one_or_none()
    if not exc:
        raise HTTPException(status_code=404, detail="Exception record not found")
    return exc
