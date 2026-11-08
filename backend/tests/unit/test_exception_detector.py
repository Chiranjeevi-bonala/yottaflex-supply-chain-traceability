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
from app.models.recall_affected_finished_lot import RecallAffectedFinishedLot
from app.models.recall_affected_delivery import RecallAffectedDelivery
from app.engine.exception_detector import ExceptionDetector

def test_exception_detector_all_four_scenarios(db_session: Session):
    # Setup base entities
    db_session.add(Supplier(supplier_id="SUP-01", name="Sup", country="US", category="INGREDIENT", contact_email="a@a.com"))
    db_session.add(Product(product_id="PROD-01", name="Prod", sku="SKU-01", category="BEVERAGE", uom="UNIT", shelf_life_days=100))
    db_session.add(ProductionOrder(order_id="WO-01", product_id="PROD-01", planned_qty=1000.0, actual_qty=1000.0, start_date=date(2026,1,1), location="PLANT-1"))
    
    # Finished lot 1: has missing input lot (EC-01)
    db_session.add(FinishedLot(lot_id="FINLOT-EC01", order_id="WO-01", product_id="PROD-01", quantity_produced=500.0, qty_remaining=500.0, production_date=date(2026,1,2), expiry_date=date(2026,6,2)))
    db_session.add(LotGenealogy(finished_lot_id="FINLOT-EC01", material_lot_id_ref="RAWLOT-GHOST-999", material_lot_id=None, qty_contributed=200.0))

    # Finished lot 2: has delivery overrun (EC-02)
    db_session.add(FinishedLot(lot_id="FINLOT-EC02", order_id="WO-01", product_id="PROD-01", quantity_produced=100.0, qty_remaining=0.0, production_date=date(2026,1,2), expiry_date=date(2026,6,2)))
    db_session.add(Shipment(shipment_id="SHP-EC02", finished_lot_id="FINLOT-EC02", carrier="UPS", ship_date=date(2026,1,3), expected_delivery_date=date(2026,1,5), qty_shipped=150.0))
    db_session.add(Customer(customer_id="CUST-01", name="Kroger", country="US", region="NA", contact_email="k@k.com", tier="SILVER"))
    # Delivered 150kg when only 100kg produced => 50kg overrun!
    db_session.add(Delivery(delivery_id="DEL-EC02", shipment_id="SHP-EC02", customer_id="CUST-01", qty_delivered=150.0, delivery_date=date(2026,1,5)))

    # Recall scenario for EC-03 and EC-04
    db_session.add(RecallCase(recall_id="REC-TEST-01", trigger_type="FINISHED_LOT", trigger_lot_id="FINLOT-EC04", reason="Toxin", status="OPEN"))
    # Finished lot 3: in recall scope but remains IN_WAREHOUSE with stock (EC-04)
    db_session.add(FinishedLot(lot_id="FINLOT-EC04", order_id="WO-01", product_id="PROD-01", quantity_produced=400.0, qty_remaining=150.0, production_date=date(2026,1,2), expiry_date=date(2026,6,2), status="IN_WAREHOUSE"))
    db_session.add(RecallAffectedFinishedLot(recall_id="REC-TEST-01", finished_lot_id="FINLOT-EC04", qty_in_scope=400.0))

    # Delivery in recall scope where customer was NEVER notified (EC-03)
    db_session.add(RecallAffectedDelivery(recall_id="REC-TEST-01", delivery_id="DEL-EC02", qty_in_scope=150.0))

    db_session.commit()

    # Run detectors
    report = ExceptionDetector.run_all_detectors(db_session)
    assert report["total_detected_exceptions"] >= 4
    assert len(report["exceptions_by_category"]["missing_input_lots"]) == 1
    assert report["exceptions_by_category"]["missing_input_lots"][0]["missing_material_lot_ref"] == "RAWLOT-GHOST-999"

    assert len(report["exceptions_by_category"]["delivery_overruns"]) == 1
    assert report["exceptions_by_category"]["delivery_overruns"][0]["overrun_quantity"] == 50.0

    assert len(report["exceptions_by_category"]["missed_customers"]) == 1
    assert report["exceptions_by_category"]["missed_customers"][0]["customer_id"] == "CUST-01"

    assert len(report["exceptions_by_category"]["unquarantined_inventory"]) == 1
    assert report["exceptions_by_category"]["unquarantined_inventory"][0]["finished_lot_id"] == "FINLOT-EC04"

