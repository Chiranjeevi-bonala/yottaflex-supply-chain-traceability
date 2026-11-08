from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.delivery import Delivery
from app.schemas.entities import DeliveryResponse

router = APIRouter(prefix="/api/deliveries", tags=["Deliveries"])

@router.get("", response_model=List[DeliveryResponse])
def list_deliveries(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    shipment_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(Delivery)
    if shipment_id:
        query = query.where(Delivery.shipment_id == shipment_id)
    if customer_id:
        query = query.where(Delivery.customer_id == customer_id)
    if status:
        query = query.where(Delivery.status == status)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()

@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: str, db: Session = Depends(get_db)):
    d = db.execute(select(Delivery).where(Delivery.delivery_id == delivery_id)).scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return d

