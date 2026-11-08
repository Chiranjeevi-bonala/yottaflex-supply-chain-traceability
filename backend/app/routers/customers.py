from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.customer import Customer
from app.models.delivery import Delivery
from app.schemas.entities import CustomerResponse, DeliveryResponse

router = APIRouter(prefix="/api/customers", tags=["Customers & Deliveries"])

@router.get("", response_model=List[CustomerResponse])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    tier: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(Customer)
    if tier:
        query = query.where(Customer.tier == tier)
    if region:
        query = query.where(Customer.region == region)
    if country:
        query = query.where(Customer.country == country)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    cust = db.execute(select(Customer).where(Customer.customer_id == customer_id)).scalar_one_or_none()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    return cust

@router.get("/{customer_id}/deliveries", response_model=List[DeliveryResponse])
def get_customer_deliveries(
    customer_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = select(Delivery).where(Delivery.customer_id == customer_id).offset(skip).limit(limit)
    return db.execute(query).scalars().all()
