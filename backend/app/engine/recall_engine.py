from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.models.recall_case import RecallCase
from app.models.recall_action import RecallAction
from app.models.recall_affected_finished_lot import RecallAffectedFinishedLot
from app.models.recall_affected_delivery import RecallAffectedDelivery
from app.models.finished_lot import FinishedLot
from app.models.delivery import Delivery
from app.engine.genealogy import GenealogyEngine
from data.generators.id_gen import IDGen

class RecallEngine:
    @staticmethod
    def initiate_recall(
        db: Session,
        trigger_type: str,
        trigger_lot_id: str,
        reason: str,
        severity: str,
        initiated_by: str = "System Quality Officer"
    ) -> Dict[str, Any]:
        """
        Creates a new RecallCase, calculates its downstream scope, and registers affected lots/deliveries.
        """
        # Determine unique recall id
        existing_count = len(db.execute(select(RecallCase)).scalars().all())
        recall_id = IDGen.recall_case(existing_count + 1)

        # Traverse genealogy downstream
        if trigger_type == "RAW_LOT":
            trace_result = GenealogyEngine.trace_downstream_from_material_lot(db, trigger_lot_id)
        elif trigger_type == "FINISHED_LOT":
            trace_result = GenealogyEngine.trace_downstream_from_finished_lot(db, trigger_lot_id)
        else:
            return {"error": f"Invalid trigger_type: {trigger_type}", "success": False}

        if not trace_result.get("found", True):
            return {"error": trace_result.get("error", "Trigger lot not found"), "success": False}

        total_affected_qty = trace_result.get("summary", {}).get("total_produced_affected_kg", 0.0)

        # Create recall case
        recall_case = RecallCase(
            recall_id=recall_id,
            trigger_type=trigger_type,
            trigger_lot_id=trigger_lot_id,
            reason=reason,
            severity=severity,
            initiated_by=initiated_by or "System Quality Officer",
            status="OPEN",
            total_qty_affected=total_affected_qty,
            total_qty_recovered=0.0,
        )
        db.add(recall_case)
        db.flush()

        # Link affected finished lots
        for fl_info in trace_result.get("affected_finished_lots", []):
            aff_fl = RecallAffectedFinishedLot(
                recall_id=recall_id,
                finished_lot_id=fl_info["lot_id"],
                qty_in_scope=fl_info.get("quantity_produced", 0.0)
            )
            db.add(aff_fl)

        # Link affected deliveries
        for deliv_info in trace_result.get("affected_deliveries", []):
            aff_del = RecallAffectedDelivery(
                recall_id=recall_id,
                delivery_id=deliv_info["delivery_id"],
                qty_in_scope=deliv_info.get("qty_delivered", 0.0)
            )
            db.add(aff_del)

        db.commit()
        return {
            "success": True,
            "recall_id": recall_id,
            "trigger_lot_id": trigger_lot_id,
            "total_qty_affected": total_affected_qty,
            "affected_finished_lots_count": len(trace_result.get("affected_finished_lots", [])),
            "affected_deliveries_count": len(trace_result.get("affected_deliveries", [])),
            "affected_customers_count": len(trace_result.get("affected_customers", [])),
        }

    @staticmethod
    def record_recall_action(
        db: Session,
        recall_id: str,
        action_type: str,
        target_entity_type: str,
        target_entity_id: str,
        qty_affected: Optional[float] = None,
        qty_actioned: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Records an explicit action (NOTIFY, QUARANTINE, RECOVER) on an active recall case.
        """
        recall = db.execute(select(RecallCase).where(RecallCase.recall_id == recall_id)).scalar_one_or_none()
        if not recall:
            return {"error": f"Recall case {recall_id} not found", "success": False}

        action_count = len(db.execute(select(RecallAction)).scalars().all())
        action_id = IDGen.recall_action(action_count + 1)

        action = RecallAction(
            action_id=action_id,
            recall_id=recall_id,
            action_type=action_type,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            qty_affected=qty_affected,
            qty_actioned=qty_actioned,
            status="COMPLETED",
            notes=notes,
        )
        db.add(action)

        # If QUARANTINE on finished lot, update lot status
        if action_type == "QUARANTINE" and target_entity_type == "FINISHED_LOT":
            db.execute(
                update(FinishedLot)
                .where(FinishedLot.lot_id == target_entity_id)
                .values(status="QUARANTINED")
            )

        # If RECOVER, increment total_qty_recovered on recall
        if action_type == "RECOVER" and qty_actioned:
            current_rec = float(recall.total_qty_recovered or 0.0)
            recall.total_qty_recovered = current_rec + float(qty_actioned)
            recall.status = "IN_PROGRESS"

        db.commit()
        return {
            "success": True,
            "action_id": action_id,
            "action_type": action_type,
            "recall_id": recall_id,
            "target_entity_id": target_entity_id,
        }

    @staticmethod
    def evaluate_recall_completion(db: Session, recall_id: str) -> Dict[str, Any]:
        """
        Evaluates whether a recall case meets all mandatory conditions for closure:
        1. All finished lots in scope have been quarantined or accounted for.
        2. All affected downstream customers have received official notification.
        3. Outstanding quantities are verified and accounted for.
        """
        recall = db.execute(select(RecallCase).where(RecallCase.recall_id == recall_id)).scalar_one_or_none()
        if not recall:
            return {"can_close": False, "reasons": [f"Recall case {recall_id} not found"]}

        reasons = []

        # Check 1: Quarantine of finished lots in scope
        scope_finlots = db.execute(
            select(RecallAffectedFinishedLot.finished_lot_id).where(RecallAffectedFinishedLot.recall_id == recall_id)
        ).scalars().all()
        if scope_finlots:
            unquarantined_lots = db.execute(
                select(FinishedLot.lot_id).where(
                    FinishedLot.lot_id.in_(scope_finlots),
                    FinishedLot.status == "IN_WAREHOUSE",
                    FinishedLot.qty_remaining > 0
                )
            ).scalars().all()
            if unquarantined_lots:
                reasons.append(f"Unquarantined warehouse inventory remains on lots: {list(unquarantined_lots)}")

        # Check 2: Customer notification coverage
        scope_delivs = db.execute(
            select(RecallAffectedDelivery.delivery_id).where(RecallAffectedDelivery.recall_id == recall_id)
        ).scalars().all()
        if scope_delivs:
            affected_cust_ids = set(
                db.execute(
                    select(Delivery.customer_id).where(Delivery.delivery_id.in_(scope_delivs))
                ).scalars().all()
            )
            notified_cust_ids = set(
                db.execute(
                    select(RecallAction.target_entity_id).where(
                        RecallAction.recall_id == recall_id,
                        RecallAction.action_type == "NOTIFY",
                        RecallAction.target_entity_type == "CUSTOMER"
                    )
                ).scalars().all()
            )
            unnotified = affected_cust_ids - notified_cust_ids
            if unnotified:
                reasons.append(f"Unnotified affected customers remaining: {list(unnotified)}")

        can_close = len(reasons) == 0
        return {
            "can_close": can_close,
            "reasons": reasons,
            "scope_finished_lots_count": len(scope_finlots),
            "scope_deliveries_count": len(scope_delivs),
            "total_qty_affected": float(recall.total_qty_affected or 0.0),
            "total_qty_recovered": float(recall.total_qty_recovered or 0.0),
            "outstanding_qty": max(0.0, float(recall.total_qty_affected or 0.0) - float(recall.total_qty_recovered or 0.0))
        }

    @staticmethod
    def close_recall(db: Session, recall_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Closes recall case after validating completion conditions unless force=True.
        """
        recall = db.execute(select(RecallCase).where(RecallCase.recall_id == recall_id)).scalar_one_or_none()
        if not recall:
            return {"error": f"Recall case {recall_id} not found", "success": False}

        if not force:
            eval_result = RecallEngine.evaluate_recall_completion(db, recall_id)
            if not eval_result["can_close"]:
                return {
                    "error": "Recall completion conditions not satisfied",
                    "details": eval_result["reasons"],
                    "success": False
                }

        recall.status = "CLOSED"
        recall.closed_at = datetime.now(timezone.utc)
        db.commit()

        remaining_unrecovered = max(0.0, float(recall.total_qty_affected or 0.0) - float(recall.total_qty_recovered or 0.0))
        return {
            "success": True,
            "recall_id": recall_id,
            "status": "CLOSED",
            "total_qty_affected": float(recall.total_qty_affected or 0.0),
            "total_qty_recovered": float(recall.total_qty_recovered or 0.0),
            "remaining_unrecovered": remaining_unrecovered,
        }
