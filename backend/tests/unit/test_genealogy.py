import pytest
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
from app.engine.genealogy import GenealogyEngine

def test_genealogy_downstream_and_upstream(db_session: Session):
    # Setup test supply chain data
    supp = Supplier(
        supplier_id="SUP-000001",
        name="Global Agro Chemical",
        country="United States",
        category="INGREDIENT",
        contact_email="supply@agro.com",
        is_active=True,
    )
    db_session.add(supp)

    prod = Product(
        product_id="PROD-000001",
        name="Protein Shake",
        sku="SKU-PROT-01",
        category="BEVERAGE",
        uom="UNIT",
        shelf_life_days=180,
        is_active=True,
    )
    db_session.add(prod)

    raw_lot = MaterialLot(
        lot_id="RAWLOT-SUP-000001-2026-000001",
        supplier_id="SUP-000001",
        material_type="Soy Protein Isolate",
        quantity_kg=5000.0,
        qty_remaining_kg=3000.0,
        unit="KG",
        receipt_date=date(2026, 1, 10),
        expiry_date=date(2026, 12, 10),
        status="IN_STOCK",
    )
    db_session.add(raw_lot)

    order = ProductionOrder(
        order_id="WO-2026-000001",
        product_id="PROD-000001",
        planned_qty=2000.0,
        actual_qty=2000.0,
        start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 3),
        status="COMPLETED",
        location="PLANT-EAST-LINE-01",
    )
    db_session.add(order)

    fin_lot = FinishedLot(
        lot_id="FINLOT-2026-000001",
        order_id="WO-2026-000001",
        product_id="PROD-000001",
        quantity_produced=2000.0,
        qty_remaining=500.0,
        production_date=date(2026, 2, 3),
        expiry_date=date(2026, 8, 3),
        status="PARTIALLY_SHIPPED",
    )
    db_session.add(fin_lot)

    genealogy = LotGenealogy(
        finished_lot_id="FINLOT-2026-000001",
        material_lot_id_ref="RAWLOT-SUP-000001-2026-000001",
        material_lot_id="RAWLOT-SUP-000001-2026-000001",
        qty_contributed=500.0,
    )
    db_session.add(genealogy)

    shipment = Shipment(
        shipment_id="SHP-2026-000001",
        finished_lot_id="FINLOT-2026-000001",
        carrier="FedEx Freight",
        ship_date=date(2026, 2, 10),
        expected_delivery_date=date(2026, 2, 12),
        actual_delivery_date=date(2026, 2, 12),
        status="DELIVERED",
        qty_shipped=1500.0,
    )
    db_session.add(shipment)

    cust = Customer(
        customer_id="CUST-000001",
        name="Target Stores Distribution",
        country="United States",
        region="North America",
        contact_email="safety@target.com",
        tier="GOLD",
        is_active=True,
    )
    db_session.add(cust)

    delivery = Delivery(
        delivery_id="DEL-000001",
        shipment_id="SHP-2026-000001",
        customer_id="CUST-000001",
        qty_delivered=1500.0,
        delivery_date=date(2026, 2, 12),
        status="DELIVERED",
    )
    db_session.add(delivery)
    db_session.commit()

    # Test downstream traversal from raw lot
    downstream = GenealogyEngine.trace_downstream_from_material_lot(db_session, "RAWLOT-SUP-000001-2026-000001")
    assert downstream["trigger_lot_id"] == "RAWLOT-SUP-000001-2026-000001"
    assert len(downstream["affected_finished_lots"]) == 1
    assert downstream["affected_finished_lots"][0]["lot_id"] == "FINLOT-2026-000001"
    assert len(downstream["affected_shipments"]) == 1
    assert len(downstream["affected_deliveries"]) == 1
    assert len(downstream["affected_customers"]) == 1
    assert downstream["affected_customers"][0]["customer_id"] == "CUST-000001"

    # Test upstream traversal from finished lot
    upstream = GenealogyEngine.trace_upstream_from_finished_lot(db_session, "FINLOT-2026-000001")
    assert upstream["finished_lot_id"] == "FINLOT-2026-000001"
    assert len(upstream["ingredients"]) == 1
    assert upstream["ingredients"][0]["material_lot_id"] == "RAWLOT-SUP-000001-2026-000001"
    assert len(upstream["suppliers"]) == 1
    assert upstream["suppliers"][0]["supplier_id"] == "SUP-000001"

