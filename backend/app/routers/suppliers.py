from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.supplier import Supplier
from app.schemas.entities import SupplierResponse

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])

@router.get("", response_model=List[SupplierResponse])
def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    category: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(Supplier)
    if category:
        query = query.where(Supplier.category == category)
    if country:
        query = query.where(Supplier.country == country)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()

@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    supp = db.execute(select(Supplier).where(Supplier.supplier_id == supplier_id)).scalar_one_or_none()
    if not supp:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supp

