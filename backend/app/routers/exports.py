import os
import io
import csv
import json
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from app.database import get_db
from app.models.supplier import Supplier
from app.models.material_lot import MaterialLot
from app.models.product import Product
from app.models.production_order import ProductionOrder
from app.models.finished_lot import FinishedLot
from app.models.shipment import Shipment
from app.models.customer import Customer
from app.models.delivery import Delivery
from app.models.recall_case import RecallCase

router = APIRouter(prefix="/api/exports", tags=["Exports & Data Downloads"])

ENTITY_MODELS = {
    "suppliers": Supplier,
    "material_lots": MaterialLot,
    "products": Product,
    "production_orders": ProductionOrder,
    "finished_lots": FinishedLot,
    "shipments": Shipment,
    "customers": Customer,
    "deliveries": Delivery,
    "recalls": RecallCase,
}

def row_to_dict(row):
    d = {}
    for col in row.__table__.columns:
        val = getattr(row, col.name)
        if hasattr(val, "isoformat"):
            val = val.isoformat()
        elif hasattr(val, "__float__"):
            val = float(val)
        d[col.name] = val
    return d

@router.get("/json")
def export_json(
    entity: str = Query("suppliers", description="Entity name to export: suppliers, material_lots, products, production_orders, finished_lots, shipments, customers, deliveries, recalls"),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    if entity not in ENTITY_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid entity '{entity}'. Allowed: {list(ENTITY_MODELS.keys())}")
    
    model = ENTITY_MODELS[entity]
    rows = db.execute(select(model).limit(limit)).scalars().all()
    records = [row_to_dict(r) for r in rows]

    return {
        "entity": entity,
        "count": len(records),
        "records": records
    }

@router.get("/csv")
def export_csv(
    entity: str = Query("suppliers", description="Entity name to export: suppliers, material_lots, products, production_orders, finished_lots, shipments, customers, deliveries, recalls"),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    if entity not in ENTITY_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid entity '{entity}'. Allowed: {list(ENTITY_MODELS.keys())}")
    
    model = ENTITY_MODELS[entity]
    rows = db.execute(select(model).limit(limit)).scalars().all()
    records = [row_to_dict(r) for r in rows]

    if not records:
        return Response(content="", media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={entity}.csv"})

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={entity}.csv"
    return response
