from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.product import Product
from app.models.bom import BOM
from app.schemas.entities import ProductResponse, BOMItemResponse

router = APIRouter(prefix="/api/products", tags=["Products & Recipes"])

@router.get("", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = select(Product)
    if category:
        query = query.where(Product.category == category)
    if is_active is not None:
        query = query.where(Product.is_active == is_active)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    prod = db.execute(select(Product).where(Product.product_id == product_id)).scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

@router.get("/{product_id}/bom", response_model=List[BOMItemResponse])
def get_product_bom(product_id: str, db: Session = Depends(get_db)):
    items = db.execute(select(BOM).where(BOM.product_id == product_id)).scalars().all()
    return items
