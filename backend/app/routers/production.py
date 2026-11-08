from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.production_order import ProductionOrder
from app.models.production_consumption import ProductionConsumption
from app.schemas.entities import ProductionOrderResponse

router = APIRouter(tags=["Production Orders"])

# Support both /api/production-orders and /api/production/orders

@router.get("/api/production-orders", response_model=List[ProductionOrderResponse])
@router.get("/api/production/orders", response_model=List[ProductionOrderResponse])
def list_production_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    product_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(ProductionOrder)
    if product_id:
        query = query.where(ProductionOrder.product_id == product_id)
    if status:
        query = query.where(ProductionOrder.status == status)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()

@router.get("/api/production-orders/{order_id}", response_model=ProductionOrderResponse)
@router.get("/api/production/orders/{order_id}", response_model=ProductionOrderResponse)
def get_production_order(order_id: str, db: Session = Depends(get_db)):
    order = db.execute(select(ProductionOrder).where(ProductionOrder.order_id == order_id)).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Production order not found")
    return order

@router.get("/api/production-orders/{order_id}/consumptions")
@router.get("/api/production/orders/{order_id}/consumptions")
def get_order_consumptions(order_id: str, db: Session = Depends(get_db)):
    consumptions = db.execute(
        select(ProductionConsumption).where(ProductionConsumption.order_id == order_id)
    ).scalars().all()
    return [
        {
            "consumption_id": c.consumption_id,
            "order_id": c.order_id,
            "lot_id": c.lot_id,
            "qty_consumed": float(c.qty_consumed),
            "consumed_at": c.consumed_at.isoformat() if c.consumed_at else None,
        }
        for c in consumptions
    ]
