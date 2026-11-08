from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.recall_case import RecallCase
from app.models.recall_action import RecallAction
from app.models.recall_affected_finished_lot import RecallAffectedFinishedLot
from app.models.recall_affected_delivery import RecallAffectedDelivery
from app.schemas.entities import RecallCaseResponse, RecallCaseCreate, RecallActionCreate, RecallActionResponse
from app.engine.recall_engine import RecallEngine

router = APIRouter(prefix="/api/recalls", tags=["Recalls"])

@router.get("", response_model=List[RecallCaseResponse])
def list_recalls(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(RecallCase)
    if status:
        query = query.where(RecallCase.status == status)
    if severity:
        query = query.where(RecallCase.severity == severity)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()

@router.get("/{recall_id}")
def get_recall_details(recall_id: str, db: Session = Depends(get_db)):
    recall = db.execute(select(RecallCase).where(RecallCase.recall_id == recall_id)).scalar_one_or_none()
    if not recall:
        raise HTTPException(status_code=404, detail="Recall case not found")

    actions = db.execute(select(RecallAction).where(RecallAction.recall_id == recall_id)).scalars().all()
    aff_finlots = db.execute(select(RecallAffectedFinishedLot).where(RecallAffectedFinishedLot.recall_id == recall_id)).scalars().all()
    aff_delivs = db.execute(select(RecallAffectedDelivery).where(RecallAffectedDelivery.recall_id == recall_id)).scalars().all()

    remaining = max(0.0, float(recall.total_qty_affected or 0.0) - float(recall.total_qty_recovered or 0.0))

    return {
        "recall_case": {
            "recall_id": recall.recall_id,
            "trigger_type": recall.trigger_type,
            "trigger_lot_id": recall.trigger_lot_id,
            "reason": recall.reason,
            "severity": recall.severity,
            "status": recall.status,
            "initiated_by": recall.initiated_by,
            "initiated_at": recall.initiated_at.isoformat() if recall.initiated_at else None,
            "closed_at": recall.closed_at.isoformat() if recall.closed_at else None,
            "total_qty_affected": float(recall.total_qty_affected or 0.0),
            "total_qty_recovered": float(recall.total_qty_recovered or 0.0),
            "remaining_unrecovered_qty": remaining,
        },
        "affected_finished_lots": [
            {"finished_lot_id": f.finished_lot_id, "qty_in_scope": float(f.qty_in_scope)}
            for f in aff_finlots
        ],
        "affected_deliveries": [
            {"delivery_id": d.delivery_id, "qty_in_scope": float(d.qty_in_scope)}
            for d in aff_delivs
        ],
        "actions_log": [
            {
                "action_id": a.action_id,
                "action_type": a.action_type,
                "target_entity_type": a.target_entity_type,
                "target_entity_id": a.target_entity_id,
                "qty_affected": float(a.qty_affected) if a.qty_affected else None,
                "qty_actioned": float(a.qty_actioned) if a.qty_actioned else None,
                "status": a.status,
                "notes": a.notes,
                "actioned_at": a.actioned_at.isoformat() if a.actioned_at else None,
            }
            for a in actions
        ]
    }

@router.get("/{recall_id}/scope")
def get_recall_scope(recall_id: str, db: Session = Depends(get_db)):
    recall = db.execute(select(RecallCase).where(RecallCase.recall_id == recall_id)).scalar_one_or_none()
    if not recall:
        raise HTTPException(status_code=404, detail="Recall case not found")

    aff_finlots = db.execute(select(RecallAffectedFinishedLot).where(RecallAffectedFinishedLot.recall_id == recall_id)).scalars().all()
    aff_delivs = db.execute(select(RecallAffectedDelivery).where(RecallAffectedDelivery.recall_id == recall_id)).scalars().all()

    return {
        "recall_id": recall_id,
        "trigger_type": recall.trigger_type,
        "trigger_lot_id": recall.trigger_lot_id,
        "total_qty_affected": float(recall.total_qty_affected or 0.0),
        "affected_finished_lots": [
            {"finished_lot_id": f.finished_lot_id, "qty_in_scope": float(f.qty_in_scope)}
            for f in aff_finlots
        ],
        "affected_deliveries": [
            {"delivery_id": d.delivery_id, "qty_in_scope": float(d.qty_in_scope)}
            for d in aff_delivs
        ]
    }

@router.get("/{recall_id}/actions", response_model=List[RecallActionResponse])
def get_recall_actions(recall_id: str, db: Session = Depends(get_db)):
    recall = db.execute(select(RecallCase).where(RecallCase.recall_id == recall_id)).scalar_one_or_none()
    if not recall:
        raise HTTPException(status_code=404, detail="Recall case not found")
    actions = db.execute(select(RecallAction).where(RecallAction.recall_id == recall_id)).scalars().all()
    return actions

@router.get("/{recall_id}/completion-check")
def check_recall_completion(recall_id: str, db: Session = Depends(get_db)):
    result = RecallEngine.evaluate_recall_completion(db, recall_id)
    return result

@router.post("", status_code=status.HTTP_201_CREATED)
def create_recall(payload: RecallCaseCreate, db: Session = Depends(get_db)):
    result = RecallEngine.initiate_recall(
        db=db,
        trigger_type=payload.trigger_type,
        trigger_lot_id=payload.trigger_lot_id,
        reason=payload.reason,
        severity=payload.severity,
        initiated_by=payload.initiated_by
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.post("/{recall_id}/actions", status_code=status.HTTP_201_CREATED)
def add_recall_action(recall_id: str, payload: RecallActionCreate, db: Session = Depends(get_db)):
    result = RecallEngine.record_recall_action(
        db=db,
        recall_id=recall_id,
        action_type=payload.action_type,
        target_entity_type=payload.target_entity_type,
        target_entity_id=payload.target_entity_id,
        qty_affected=payload.qty_affected,
        qty_actioned=payload.qty_actioned,
        notes=payload.notes,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.post("/{recall_id}/close")
def close_recall_case(recall_id: str, force: bool = Query(False), db: Session = Depends(get_db)):
    result = RecallEngine.close_recall(db, recall_id, force=force)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
