from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.finished_lot import FinishedLot
from app.models.lot_genealogy import LotGenealogy
from app.models.shipment import Shipment
from app.models.delivery import Delivery
from app.models.recall_case import RecallCase
from app.models.recall_affected_finished_lot import RecallAffectedFinishedLot
from app.models.recall_affected_delivery import RecallAffectedDelivery
from app.models.recall_action import RecallAction

class ExceptionDetector:
    @staticmethod
    def detect_missing_input_lots(db: Session) -> List[Dict[str, Any]]:
        """
        EC-01: Finished lot references missing input lot.
        Identifies genealogy records where the raw material lot does not exist in the database.
        """
        # Find genealogy where material_lot_id is null
        records = db.execute(
            select(LotGenealogy).where(LotGenealogy.material_lot_id.is_(None))
        ).scalars().all()

        results = []
        for r in records:
            results.append({
                "issue_type": "MISSING_INPUT_LOT",
                "finished_lot_id": r.finished_lot_id,
                "missing_material_lot_ref": r.material_lot_id_ref,
                "qty_contributed": float(r.qty_contributed),
                "operational_impact": "Loss of upstream supplier traceability; unknown ingredient provenance",
                "recommended_action": "Quarantine finished lot immediately; verify production batch records against physical log",
            })
        return results

    @staticmethod
    def detect_delivery_overruns(db: Session) -> List[Dict[str, Any]]:
        """
        EC-02: Delivered quantity exceeds produced quantity.
        Identifies finished lots where the sum of deliveries exceeds produced quantity.
        """
        # Aggregate deliveries by finished lot
        stmt = (
            select(
                FinishedLot.lot_id,
                FinishedLot.quantity_produced,
                func.sum(Delivery.qty_delivered).label("total_delivered")
            )
            .join(Shipment, Shipment.finished_lot_id == FinishedLot.lot_id)
            .join(Delivery, Delivery.shipment_id == Shipment.shipment_id)
            .group_by(FinishedLot.lot_id, FinishedLot.quantity_produced)
            .having(func.sum(Delivery.qty_delivered) > FinishedLot.quantity_produced)
        )
        rows = db.execute(stmt).all()

        results = []
        for row in rows:
            lot_id, produced, delivered = row
            overrun = float(delivered) - float(produced)
            results.append({
                "issue_type": "DELIVERY_OVERRUN",
                "finished_lot_id": lot_id,
                "quantity_produced": float(produced),
                "total_delivered": float(delivered),
                "overrun_quantity": round(overrun, 3),
                "operational_impact": "Physical phantom inventory; unrecorded production or duplicate shipping scanning",
                "recommended_action": "Freeze carrier invoices; conduct physical audit of warehouse and carrier manifests",
            })
        return results

    @staticmethod
    def detect_missed_customers(db: Session) -> List[Dict[str, Any]]:
        """
        EC-03: Recall misses a downstream customer.
        Identifies customers who received deliveries of recalled lots but received no NOTIFY action.
        """
        active_recalls = db.execute(
            select(RecallCase).where(RecallCase.status.in_(["OPEN", "IN_PROGRESS"]))
        ).scalars().all()

        results = []
        for recall in active_recalls:
            # All deliveries in recall scope
            affected_delivs = db.execute(
                select(RecallAffectedDelivery).where(RecallAffectedDelivery.recall_id == recall.recall_id)
            ).scalars().all()
            aff_deliv_ids = [ad.delivery_id for ad in affected_delivs]

            if not aff_deliv_ids:
                continue

            deliveries = db.execute(
                select(Delivery).where(Delivery.delivery_id.in_(aff_deliv_ids))
            ).scalars().all()
            customers_in_scope = {d.customer_id: d for d in deliveries}

            # All customers notified in this recall
            notified_actions = db.execute(
                select(RecallAction).where(
                    RecallAction.recall_id == recall.recall_id,
                    RecallAction.action_type == "NOTIFY",
                    RecallAction.target_entity_type == "CUSTOMER"
                )
            ).scalars().all()
            notified_customer_ids = set(a.target_entity_id for a in notified_actions)

            # Find missed customers
            missed = set(customers_in_scope.keys()) - notified_customer_ids
            for cid in missed:
                matching_d = customers_in_scope[cid]
                results.append({
                    "issue_type": "MISSED_CUSTOMER",
                    "recall_id": recall.recall_id,
                    "customer_id": cid,
                    "delivery_id": matching_d.delivery_id,
                    "qty_delivered": float(matching_d.qty_delivered),
                    "operational_impact": "Downstream consumer health hazard; legal non-compliance with statutory recall notices",
                    "recommended_action": "Dispatch emergency certified recall communication; escalate to regulatory affairs",
                })
        return results

    @staticmethod
    def detect_unquarantined_inventory(db: Session) -> List[Dict[str, Any]]:
        """
        EC-04: Recalled inventory remains available for sale.
        Identifies finished lots included in active recalls that still have IN_WAREHOUSE status and remaining stock.
        """
        active_recalls = db.execute(
            select(RecallCase).where(RecallCase.status.in_(["OPEN", "IN_PROGRESS"]))
        ).scalars().all()

        results = []
        for recall in active_recalls:
            aff_finlots = db.execute(
                select(RecallAffectedFinishedLot).where(RecallAffectedFinishedLot.recall_id == recall.recall_id)
            ).scalars().all()
            finlot_ids = [a.finished_lot_id for a in aff_finlots]

            if not finlot_ids:
                continue

            lots = db.execute(
                select(FinishedLot).where(
                    FinishedLot.lot_id.in_(finlot_ids),
                    FinishedLot.status == "IN_WAREHOUSE",
                    FinishedLot.qty_remaining > 0
                )
            ).scalars().all()

            for lot in lots:
                results.append({
                    "issue_type": "INVENTORY_NOT_QUARANTINED",
                    "recall_id": recall.recall_id,
                    "finished_lot_id": lot.lot_id,
                    "qty_remaining_available": float(lot.qty_remaining),
                    "current_status": lot.status,
                    "operational_impact": "Active risk of accidental shipment of contaminated products to new customers",
                    "recommended_action": "Execute immediate ERP order hold on lot; tag physical bins with red quarantine tape",
                })
        return results

    @classmethod
    def run_all_detectors(cls, db: Session) -> Dict[str, Any]:
        missing_input = cls.detect_missing_input_lots(db)
        overruns = cls.detect_delivery_overruns(db)
        missed_customers = cls.detect_missed_customers(db)
        unquarantined = cls.detect_unquarantined_inventory(db)

        total_anomalies = len(missing_input) + len(overruns) + len(missed_customers) + len(unquarantined)
        return {
            "total_detected_exceptions": total_anomalies,
            "exceptions_by_category": {
                "missing_input_lots": missing_input,
                "delivery_overruns": overruns,
                "missed_customers": missed_customers,
                "unquarantined_inventory": unquarantined,
            },
            "status": "ALERT" if total_anomalies > 0 else "CLEAN"
        }

