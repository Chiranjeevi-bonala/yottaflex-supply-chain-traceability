from typing import Dict, List, Any, Set
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.material_lot import MaterialLot
from app.models.finished_lot import FinishedLot
from app.models.lot_genealogy import LotGenealogy
from app.models.shipment import Shipment
from app.models.delivery import Delivery
from app.models.customer import Customer
from app.models.supplier import Supplier

class GenealogyEngine:
    @staticmethod
    def trace_downstream_from_material_lot(db: Session, raw_lot_id: str) -> Dict[str, Any]:
        """
        Traverses downstream from raw material lot:
        MaterialLot -> FinishedLots -> Shipments -> Deliveries -> Customers
        """
        raw_lot = db.execute(select(MaterialLot).where(MaterialLot.lot_id == raw_lot_id)).scalar_one_or_none()
        if not raw_lot:
            return {"error": f"Material lot {raw_lot_id} not found", "found": False}

        # 1. Find finished lots linked to this raw lot
        genealogy_stmt = select(LotGenealogy).where(
            (LotGenealogy.material_lot_id == raw_lot_id) | (LotGenealogy.material_lot_id_ref == raw_lot_id)
        )
        genealogy_records = db.execute(genealogy_stmt).scalars().all()
        finlot_ids = list(set(g.finished_lot_id for g in genealogy_records))

        finlots = db.execute(select(FinishedLot).where(FinishedLot.lot_id.in_(finlot_ids))).scalars().all() if finlot_ids else []

        # 2. Find shipments for these finished lots
        shipments = db.execute(select(Shipment).where(Shipment.finished_lot_id.in_(finlot_ids))).scalars().all() if finlot_ids else []
        shipment_ids = [s.shipment_id for s in shipments]

        # 3. Find deliveries
        deliveries = db.execute(select(Delivery).where(Delivery.shipment_id.in_(shipment_ids))).scalars().all() if shipment_ids else []
        customer_ids = list(set(d.customer_id for d in deliveries))

        # 4. Find customers
        customers = db.execute(select(Customer).where(Customer.customer_id.in_(customer_ids))).scalars().all() if customer_ids else []

        total_produced_affected = sum(float(fl.quantity_produced) for fl in finlots)
        total_delivered_affected = sum(float(d.qty_delivered) for d in deliveries)

        return {
            "trigger_lot_id": raw_lot_id,
            "trigger_type": "RAW_LOT",
            "material_type": raw_lot.material_type,
            "supplier_id": raw_lot.supplier_id,
            "affected_finished_lots": [
                {
                    "lot_id": fl.lot_id,
                    "product_id": fl.product_id,
                    "quantity_produced": float(fl.quantity_produced),
                    "status": fl.status,
                    "production_date": fl.production_date.isoformat(),
                }
                for fl in finlots
            ],
            "affected_shipments": [
                {
                    "shipment_id": s.shipment_id,
                    "finished_lot_id": s.finished_lot_id,
                    "carrier": s.carrier,
                    "qty_shipped": float(s.qty_shipped),
                    "ship_date": s.ship_date.isoformat(),
                }
                for s in shipments
            ],
            "affected_deliveries": [
                {
                    "delivery_id": d.delivery_id,
                    "shipment_id": d.shipment_id,
                    "customer_id": d.customer_id,
                    "qty_delivered": float(d.qty_delivered),
                    "delivery_date": d.delivery_date.isoformat(),
                }
                for d in deliveries
            ],
            "affected_customers": [
                {
                    "customer_id": c.customer_id,
                    "name": c.name,
                    "tier": c.tier,
                    "contact_email": c.contact_email,
                }
                for c in customers
            ],
            "summary": {
                "total_finished_lots": len(finlots),
                "total_shipments": len(shipments),
                "total_deliveries": len(deliveries),
                "total_customers": len(customers),
                "total_produced_affected_kg": total_produced_affected,
                "total_delivered_affected_kg": total_delivered_affected,
            }
        }

    @staticmethod
    def trace_downstream_from_finished_lot(db: Session, finished_lot_id: str) -> Dict[str, Any]:
        """
        Traverses downstream from finished lot:
        FinishedLot -> Shipments -> Deliveries -> Customers
        """
        flot = db.execute(select(FinishedLot).where(FinishedLot.lot_id == finished_lot_id)).scalar_one_or_none()
        if not flot:
            return {"error": f"Finished lot {finished_lot_id} not found", "found": False}

        shipments = db.execute(select(Shipment).where(Shipment.finished_lot_id == finished_lot_id)).scalars().all()
        shipment_ids = [s.shipment_id for s in shipments]

        deliveries = db.execute(select(Delivery).where(Delivery.shipment_id.in_(shipment_ids))).scalars().all() if shipment_ids else []
        customer_ids = list(set(d.customer_id for d in deliveries))

        customers = db.execute(select(Customer).where(Customer.customer_id.in_(customer_ids))).scalars().all() if customer_ids else []

        total_produced_affected = float(flot.quantity_produced)
        total_delivered_affected = sum(float(d.qty_delivered) for d in deliveries)

        return {
            "trigger_lot_id": finished_lot_id,
            "trigger_type": "FINISHED_LOT",
            "product_id": flot.product_id,
            "affected_finished_lots": [
                {
                    "lot_id": flot.lot_id,
                    "product_id": flot.product_id,
                    "quantity_produced": total_produced_affected,
                    "status": flot.status,
                    "production_date": flot.production_date.isoformat(),
                }
            ],
            "affected_shipments": [
                {
                    "shipment_id": s.shipment_id,
                    "finished_lot_id": s.finished_lot_id,
                    "carrier": s.carrier,
                    "qty_shipped": float(s.qty_shipped),
                    "ship_date": s.ship_date.isoformat(),
                }
                for s in shipments
            ],
            "affected_deliveries": [
                {
                    "delivery_id": d.delivery_id,
                    "shipment_id": d.shipment_id,
                    "customer_id": d.customer_id,
                    "qty_delivered": float(d.qty_delivered),
                    "delivery_date": d.delivery_date.isoformat(),
                }
                for d in deliveries
            ],
            "affected_customers": [
                {
                    "customer_id": c.customer_id,
                    "name": c.name,
                    "tier": c.tier,
                    "contact_email": c.contact_email,
                }
                for c in customers
            ],
            "summary": {
                "total_finished_lots": 1,
                "total_shipments": len(shipments),
                "total_deliveries": len(deliveries),
                "total_customers": len(customers),
                "total_produced_affected_kg": total_produced_affected,
                "total_delivered_affected_kg": total_delivered_affected,
            }
        }

    @staticmethod
    def trace_upstream_from_finished_lot(db: Session, finished_lot_id: str) -> Dict[str, Any]:
        """
        Traverses upstream from finished lot:
        FinishedLot -> LotGenealogy -> MaterialLots -> Suppliers
        """
        flot = db.execute(select(FinishedLot).where(FinishedLot.lot_id == finished_lot_id)).scalar_one_or_none()
        if not flot:
            return {"error": f"Finished lot {finished_lot_id} not found", "found": False}

        genealogy_records = db.execute(
            select(LotGenealogy).where(LotGenealogy.finished_lot_id == finished_lot_id)
        ).scalars().all()

        raw_lot_refs = [g.material_lot_id_ref for g in genealogy_records]
        raw_lots = db.execute(select(MaterialLot).where(MaterialLot.lot_id.in_(raw_lot_refs))).scalars().all() if raw_lot_refs else []
        supplier_ids = list(set(r.supplier_id for r in raw_lots))
        suppliers = db.execute(select(Supplier).where(Supplier.supplier_id.in_(supplier_ids))).scalars().all() if supplier_ids else []

        return {
            "finished_lot_id": finished_lot_id,
            "product_id": flot.product_id,
            "quantity_produced": float(flot.quantity_produced),
            "production_date": flot.production_date.isoformat(),
            "status": flot.status,
            "ingredients": [
                {
                    "material_lot_id_ref": g.material_lot_id_ref,
                    "material_lot_id": g.material_lot_id,
                    "qty_contributed": float(g.qty_contributed),
                    "is_missing_in_db": g.material_lot_id is None,
                }
                for g in genealogy_records
            ],
            "raw_material_lots": [
                {
                    "lot_id": r.lot_id,
                    "supplier_id": r.supplier_id,
                    "material_type": r.material_type,
                    "receipt_date": r.receipt_date.isoformat(),
                }
                for r in raw_lots
            ],
            "suppliers": [
                {
                    "supplier_id": s.supplier_id,
                    "name": s.name,
                    "country": s.country,
                }
                for s in suppliers
            ]
        }
