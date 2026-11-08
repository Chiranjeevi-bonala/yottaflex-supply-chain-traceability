from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.material_lot import MaterialLot
from app.schemas.entities import MaterialLotResponse
from app.engine.genealogy import GenealogyEngine

router = APIRouter(prefix="/api/material-lots", tags=["Material Lots"])

@router.get("", response_model=List[MaterialLotResponse])
def list_material_lots(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    supplier_id: Optional[str] = None,
    material_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(MaterialLot)
    if supplier_id:
        query = query.where(MaterialLot.supplier_id == supplier_id)
    if material_type:
        query = query.where(MaterialLot.material_type == material_type)
    if status:
        query = query.where(MaterialLot.status == status)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()

@router.get("/{lot_id}", response_model=MaterialLotResponse)
def get_material_lot(lot_id: str, db: Session = Depends(get_db)):
    lot = db.execute(select(MaterialLot).where(MaterialLot.lot_id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=404, detail="Material lot not found")
    return lot

@router.get("/{lot_id}/trace")
@router.get("/{lot_id}/downstream-trace")
def trace_material_lot_downstream(lot_id: str, db: Session = Depends(get_db)):
    """
    Traverses complete supply chain downstream:
    MaterialLot -> FinishedLots -> Shipments -> Deliveries -> Customers
    """
    res = GenealogyEngine.trace_downstream_from_material_lot(db, lot_id)
    if not res.get("found", True):
        raise HTTPException(status_code=404, detail=res.get("error"))
    return res
