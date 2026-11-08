from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.shipment import Shipment
from app.schemas.entities import ShipmentResponse

router = APIRouter(prefix="/api/shipments", tags=["Shipments"])

@router.get("", response_model=List[ShipmentResponse])
def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    finished_lot_id: Optional[str] = None,
    status: Optional[str] = None,
    carrier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(Shipment)
    if finished_lot_id:
        query = query.where(Shipment.finished_lot_id == finished_lot_id)
    if status:
        query = query.where(Shipment.status == status)
    if carrier:
        query = query.where(Shipment.carrier == carrier)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()

@router.get("/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    shp = db.execute(select(Shipment).where(Shipment.shipment_id == shipment_id)).scalar_one_or_none()
    if not shp:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shp

