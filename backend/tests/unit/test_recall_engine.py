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
from app.engine.recall_engine import RecallEngine

def test_recall_engine_lifecycle(db_session: Session):
    # Setup baseline data
    db_session.add(Supplier(supplier_id="SUP-000001", name="Sup", country="US", category="INGREDIENT", contact_email="a@a.com"))
    db_session.add(Product(product_id="PROD-000001", name="Prod", sku="SKU-01", category="BEVERAGE", uom="UNIT", shelf_life_days=100))
    db_session.add(MaterialLot(lot_id="RAWLOT-01", supplier_id="SUP-000001", material_type="Flour", quantity_kg=1000.0, qty_remaining_kg=1000.0, receipt_date=date(2026,1,1), expiry_date=date(2026,6,1)))
    db_session.add(ProductionOrder(order_id="WO-01", product_id="PROD-000001", planned_qty=500.0, actual_qty=500.0, start_date=date(2026,2,1), location="PLANT-1"))
    db_session.add(FinishedLot(lot_id="FINLOT-01", order_id="WO-01", product_id="PROD-000001", quantity_produced=500.0, qty_remaining=200.0, production_date=date(2026,2,2), expiry_date=date(2026,8,2), status="IN_WAREHOUSE"))
    db_session.add(LotGenealogy(finished_lot_id="FINLOT-01", material_lot_id_ref="RAWLOT-01", material_lot_id="RAWLOT-01", qty_contributed=500.0))
    db_session.add(Shipment(shipment_id="SHP-01", finished_lot_id="FINLOT-01", carrier="DHL", ship_date=date(2026,2,3), expected_delivery_date=date(2026,2,5), qty_shipped=300.0))
    db_session.add(Customer(customer_id="CUST-01", name="Costco", country="US", region="NA", contact_email="costco@corp.com", tier="GOLD"))
    db_session.add(Delivery(delivery_id="DEL-01", shipment_id="SHP-01", customer_id="CUST-01", qty_delivered=300.0, delivery_date=date(2026,2,5)))
    db_session.commit()

    # 1. Initiate Recall
    res = RecallEngine.initiate_recall(
        db=db_session,
        trigger_type="RAW_LOT",
        trigger_lot_id="RAWLOT-01",
        reason="Biological contamination",
        severity="CLASS_I",
        initiated_by="Quality Director"
    )
    assert res["success"] is True
    recall_id = res["recall_id"]
    assert res["affected_finished_lots_count"] == 1
    assert res["affected_customers_count"] == 1

    # 2. Record Quarantine Action
    q_res = RecallEngine.record_recall_action(
        db=db_session,
        recall_id=recall_id,
        action_type="QUARANTINE",
        target_entity_type="FINISHED_LOT",
        target_entity_id="FINLOT-01",
        qty_affected=200.0,
        qty_actioned=200.0
    )
    assert q_res["success"] is True

    # 3. Record Notify Action
    n_res = RecallEngine.record_recall_action(
        db=db_session,
        recall_id=recall_id,
        action_type="NOTIFY",
        target_entity_type="CUSTOMER",
        target_entity_id="CUST-01",
    )
    assert n_res["success"] is True

    # 4. Record Recovery Action
    rec_res = RecallEngine.record_recall_action(
        db=db_session,
        recall_id=recall_id,
        action_type="RECOVER",
        target_entity_type="FINISHED_LOT",
        target_entity_id="FINLOT-01",
        qty_actioned=500.0
    )
    assert rec_res["success"] is True

    # 5. Close Recall
    close_res = RecallEngine.close_recall(db_session, recall_id)
    assert close_res["success"] is True
    assert close_res["status"] == "CLOSED"

