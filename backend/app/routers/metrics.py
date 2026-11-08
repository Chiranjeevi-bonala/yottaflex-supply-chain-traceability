from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.engine.metrics import MetricsEngine

router = APIRouter(prefix="/api/metrics", tags=["Operational Metrics"])

@router.get("")
def get_operational_metrics(db: Session = Depends(get_db)):
    """
    Returns all 8 measurable operational evaluation metrics computed from live database records:
      - M-01: Genealogy Completeness
      - M-02: Recall Scope Accuracy
      - M-03: Customer Notification Coverage
      - M-04: Quantity Reconciliation Rate
      - M-05: Inventory Quarantine Compliance
      - M-06: Recovery Rate
      - M-07: Outstanding Recall Quantity (KG)
      - M-08: Exception Detection Rate
    """
    return MetricsEngine.calculate_operational_metrics(db)

@router.get("/recall")
def get_recall_metrics(db: Session = Depends(get_db)):
    """
    Returns specific recall lifecycle metrics (M-02, M-03, M-05, M-06, M-07).
    """
    all_metrics = MetricsEngine.calculate_operational_metrics(db)
    return {
        "M02_recall_scope_accuracy": all_metrics["M02_recall_scope_accuracy"],
        "M03_customer_notification_coverage": all_metrics["M03_customer_notification_coverage"],
        "M05_inventory_quarantine_compliance": all_metrics["M05_inventory_quarantine_compliance"],
        "M06_recovery_rate": all_metrics["M06_recovery_rate"],
        "M07_outstanding_recall_quantity_kg": all_metrics["M07_outstanding_recall_quantity_kg"],
    }

@router.get("/exceptions")
def get_exception_metrics(db: Session = Depends(get_db)):
    """
    Returns specific integrity and anomaly metrics (M-01, M-04, M-08).
    """
    all_metrics = MetricsEngine.calculate_operational_metrics(db)
    return {
        "M01_genealogy_completeness": all_metrics["M01_genealogy_completeness"],
        "M04_quantity_reconciliation_rate": all_metrics["M04_quantity_reconciliation_rate"],
        "M08_exception_detection_rate": all_metrics["M08_exception_detection_rate"],
    }
