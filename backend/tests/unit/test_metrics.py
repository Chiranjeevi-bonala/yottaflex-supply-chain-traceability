from datetime import date
from sqlalchemy.orm import Session
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.material_lot import MaterialLot
from app.models.production_order import ProductionOrder
from app.models.finished_lot import FinishedLot
from app.models.lot_genealogy import LotGenealogy
from app.models.shipment import Shipment
from app.models.customer import Customer
from app.models.delivery import Delivery
from app.models.recall_case import RecallCase
from app.models.recall_action import RecallAction
from app.models.recall_affected_finished_lot import RecallAffectedFinishedLot
from app.models.recall_affected_delivery import RecallAffectedDelivery
from app.models.exception_record import ExceptionRecord
from app.engine.metrics import MetricsEngine

def test_metrics_calculation(db_session: Session):
    # Setup test entities
    db_session.add(Supplier(supplier_id="SUP-M1", name="Sup", country="US", category="INGREDIENT", contact_email="a@a.com"))
    db_session.add(Product(product_id="PROD-M1", name="Prod", sku="SKU-M1", category="BEVERAGE", uom="UNIT", shelf_life_days=100))
    db_session.add(MaterialLot(lot_id="RAW-M1", supplier_id="SUP-M1", material_type="Flour", quantity_kg=1000.0, qty_remaining_kg=1000.0, receipt_date=date(2026,1,1), expiry_date=date(2026,6,1)))
    db_session.add(ProductionOrder(order_id="WO-M1", product_id="PROD-M1", planned_qty=1000.0, actual_qty=1000.0, start_date=date(2026,1,1), location="PLANT-1"))

    # Finished lot with valid genealogy
    db_session.add(FinishedLot(lot_id="FIN-M1", order_id="WO-M1", product_id="PROD-M1", quantity_produced=1000.0, qty_remaining=0.0, production_date=date(2026,1,2), expiry_date=date(2026,6,2), status="QUARANTINED"))
    db_session.add(LotGenealogy(finished_lot_id="FIN-M1", material_lot_id_ref="RAW-M1", material_lot_id="RAW-M1", qty_contributed=500.0))

    # Shipment and delivery
    db_session.add(Shipment(shipment_id="SHP-M1", finished_lot_id="FIN-M1", carrier="FedEx", ship_date=date(2026,1,3), expected_delivery_date=date(2026,1,5), qty_shipped=1000.0))
    db_session.add(Customer(customer_id="CUST-M1", name="Walmart", country="US", region="NA", contact_email="w@w.com", tier="GOLD"))
    db_session.add(Delivery(delivery_id="DEL-M1", shipment_id="SHP-M1", customer_id="CUST-M1", qty_delivered=1000.0, delivery_date=date(2026,1,5)))

    # Recall
    db_session.add(RecallCase(recall_id="REC-M1", trigger_type="RAW_LOT", trigger_lot_id="RAW-M1", reason="Toxin", total_qty_affected=1000.0, total_qty_recovered=800.0, status="IN_PROGRESS"))
    db_session.add(RecallAffectedFinishedLot(recall_id="REC-M1", finished_lot_id="FIN-M1", qty_in_scope=1000.0))
    db_session.add(RecallAffectedDelivery(recall_id="REC-M1", delivery_id="DEL-M1", qty_in_scope=1000.0))
    db_session.add(RecallAction(action_id="ACT-M1", recall_id="REC-M1", action_type="NOTIFY", target_entity_type="CUSTOMER", target_entity_id="CUST-M1"))
    db_session.add(RecallAction(action_id="ACT-M2", recall_id="REC-M1", action_type="QUARANTINE", target_entity_type="FINISHED_LOT", target_entity_id="FIN-M1"))
    db_session.add(RecallAction(action_id="ACT-M3", recall_id="REC-M1", action_type="RECOVER", target_entity_type="FINISHED_LOT", target_entity_id="FIN-M1", qty_actioned=800.0))

    # Ground truth record
    db_session.add(ExceptionRecord(exception_id="EXC-M1", issue_type="DELIVERY_OVERRUN", entity_type="FINISHED_LOT", entity_id="FIN-M1", impact_description="impact", expected_decision="decision", ground_truth_label={"test": 1}))

    db_session.commit()

    metrics = MetricsEngine.calculate_operational_metrics(db_session)

    assert metrics["M01_genealogy_completeness"]["value"] == 1.0
    assert metrics["M03_customer_notification_coverage"]["value"] == 1.0
    assert metrics["M04_quantity_reconciliation_rate"]["value"] == 1.0
    assert metrics["M05_inventory_quarantine_compliance"]["value"] == 1.0
    assert metrics["M06_recovery_rate"]["value"] == 0.8
    assert metrics["M07_outstanding_recall_quantity_kg"]["value"] == 200.0

