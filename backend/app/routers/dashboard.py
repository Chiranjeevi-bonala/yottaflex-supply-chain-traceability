from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.database import get_db
from app.models.supplier import Supplier
from app.models.material_lot import MaterialLot
from app.models.production_order import ProductionOrder
from app.models.finished_lot import FinishedLot
from app.models.shipment import Shipment
from app.models.customer import Customer
from app.models.delivery import Delivery
from app.models.recall_case import RecallCase
from app.engine.metrics import MetricsEngine
from app.engine.exception_detector import ExceptionDetector
from app.config import settings

router = APIRouter(prefix="/api/dashboard", tags=["Executive Dashboard"])

@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Returns executive overview metrics, master entity volume counts,
    active recall tracking, and anomaly alert summaries.
    """
    suppliers_count = db.execute(select(func.count(Supplier.supplier_id))).scalar() or 0
    material_lots_count = db.execute(select(func.count(MaterialLot.lot_id))).scalar() or 0
    orders_count = db.execute(select(func.count(ProductionOrder.order_id))).scalar() or 0
    finished_lots_count = db.execute(select(func.count(FinishedLot.lot_id))).scalar() or 0
    shipments_count = db.execute(select(func.count(Shipment.shipment_id))).scalar() or 0
    customers_count = db.execute(select(func.count(Customer.customer_id))).scalar() or 0
    deliveries_count = db.execute(select(func.count(Delivery.delivery_id))).scalar() or 0

    active_recalls = db.execute(
        select(RecallCase).where(RecallCase.status.in_(["OPEN", "IN_PROGRESS"]))
    ).scalars().all()
    closed_recalls_count = db.execute(
        select(func.count(RecallCase.recall_id)).where(RecallCase.status == "CLOSED")
    ).scalar() or 0

    tot_affected = db.execute(select(func.sum(RecallCase.total_qty_affected))).scalar() or 0.0
    tot_recovered = db.execute(select(func.sum(RecallCase.total_qty_recovered))).scalar() or 0.0

    exceptions_report = ExceptionDetector.run_all_detectors(db)
    operational_metrics = MetricsEngine.calculate_operational_metrics(db)

    return {
        "status": "healthy",
        "fixed_seed": settings.data_seed,
        "database": settings.database_url.split("://")[0],
        "volumes": {
            "suppliers": suppliers_count,
            "material_lots": material_lots_count,
            "production_orders": orders_count,
            "finished_lots": finished_lots_count,
            "shipments": shipments_count,
            "customers": customers_count,
            "deliveries": deliveries_count,
        },
        "recalls": {
            "active_recalls_count": len(active_recalls),
            "closed_recalls_count": closed_recalls_count,
            "total_qty_affected_kg": float(tot_affected),
            "total_qty_recovered_kg": float(tot_recovered),
            "outstanding_qty_kg": max(0.0, float(tot_affected) - float(tot_recovered)),
        },
        "anomalies": {
            "total_detected": exceptions_report["total_detected_exceptions"],
            "status": exceptions_report["status"],
            "by_category": {
                k: len(v) for k, v in exceptions_report["exceptions_by_category"].items()
            }
        },
        "key_metrics": {
            "genealogy_completeness": operational_metrics["M01_genealogy_completeness"]["percentage"],
            "recall_scope_accuracy": operational_metrics["M02_recall_scope_accuracy"]["percentage"],
            "customer_notification_coverage": operational_metrics["M03_customer_notification_coverage"]["percentage"],
            "quantity_reconciliation_rate": operational_metrics["M04_quantity_reconciliation_rate"]["percentage"],
            "inventory_quarantine_compliance": operational_metrics["M05_inventory_quarantine_compliance"]["percentage"],
            "recovery_rate": operational_metrics["M06_recovery_rate"]["percentage"],
        }
    }
