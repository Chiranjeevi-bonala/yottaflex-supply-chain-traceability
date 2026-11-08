from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.finished_lot import FinishedLot
from app.schemas.entities import FinishedLotResponse
from app.engine.genealogy import GenealogyEngine

router = APIRouter(prefix="/api/finished-lots", tags=["Finished Lots"])

@router.get("", response_model=List[FinishedLotResponse])
def list_finished_lots(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    product_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(FinishedLot)
    if product_id:
        query = query.where(FinishedLot.product_id == product_id)
    if status:
        query = query.where(FinishedLot.status == status)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()

@router.get("/{lot_id}", response_model=FinishedLotResponse)
def get_finished_lot(lot_id: str, db: Session = Depends(get_db)):
    flot = db.execute(select(FinishedLot).where(FinishedLot.lot_id == lot_id)).scalar_one_or_none()
    if not flot:
        raise HTTPException(status_code=404, detail="Finished lot not found")
    return flot

@router.get("/{lot_id}/genealogy")
@router.get("/{lot_id}/upstream-trace")
def trace_finished_lot_upstream(lot_id: str, db: Session = Depends(get_db)):
    """
    Traverses backward through genealogy:
    FinishedLot -> LotGenealogy -> Raw Material Lots -> Suppliers
    """
    res = GenealogyEngine.trace_upstream_from_finished_lot(db, lot_id)
    if not res.get("found", True):
        raise HTTPException(status_code=404, detail=res.get("error"))
    return res

@router.get("/{lot_id}/downstream-trace")
def trace_finished_lot_downstream(lot_id: str, db: Session = Depends(get_db)):
    """
    Traverses downstream from finished lot:
    FinishedLot -> Shipments -> Deliveries -> Customers
    """
    res = GenealogyEngine.trace_downstream_from_finished_lot(db, lot_id)
    if not res.get("found", True):
        raise HTTPException(status_code=404, detail=res.get("error"))
    return res
