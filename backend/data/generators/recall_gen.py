import random
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from data.generators.id_gen import IDGen

RECALL_REASONS = [
    "Aflatoxin B1 exceedance detected during routine microbiological screening",
    "Undeclared allergen cross-contamination identified in raw ingredient supplier lot",
    "Foreign physical contaminant (fine metal shaving) found in milling filter",
    "Chemical residue (Pesticide Chlorpyrifos) detected beyond maximum allowable threshold",
    "Pathogenic Salmonella enterica detected in post-processing environmental swab",
]

def generate_recalls(
    num_recalls: int,
    material_lots: List[Dict[str, Any]],
    genealogy: List[Dict[str, Any]],
    shipments: List[Dict[str, Any]],
    deliveries: List[Dict[str, Any]],
    finished_lots: List[Dict[str, Any]],
    rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates realistic recall cases by traversing downstream genealogy:
      Trigger MaterialLot -> FinishedLots -> Shipments -> Deliveries -> Customers
    """
    # Map genealogy: raw_lot -> list of finished_lot_ids
    finlots_by_raw = {}
    for g in genealogy:
        finlots_by_raw.setdefault(g["material_lot_id_ref"], set()).add(g["finished_lot_id"])

    # Map shipments by finished_lot_id
    shipments_by_finlot = {}
    for s in shipments:
        shipments_by_finlot.setdefault(s["finished_lot_id"], []).append(s)

    # Map deliveries by shipment_id
    deliveries_by_shipment = {}
    for d in deliveries:
        deliveries_by_shipment.setdefault(d["shipment_id"], []).append(d)

    # Index finished lots
    finlot_map = {f["lot_id"]: f for f in finished_lots}

    # Find raw lots that have downstream finished lots
    candidate_raw_lots = [lot for lot in material_lots if lot["lot_id"] in finlots_by_raw]
    if not candidate_raw_lots:
        candidate_raw_lots = material_lots[:num_recalls]

    recall_cases = []
    affected_finlot_records = []
    affected_deliv_records = []
    recall_actions = []

    action_counter = 1

    for r_idx in range(1, num_recalls + 1):
        recall_id = IDGen.recall_case(r_idx)
        trigger_lot = rng.choice(candidate_raw_lots)
        trigger_lot["is_contaminated"] = True

        trigger_lot_id = trigger_lot["lot_id"]
        reason = rng.choice(RECALL_REASONS)
        severity = rng.choice(["CLASS_I", "CLASS_II", "CLASS_III"])

        # Downstream traversal
        affected_finlot_ids = finlots_by_raw.get(trigger_lot_id, set())
        
        total_qty_affected = 0.0
        affected_deliv_ids = []
        affected_customer_ids = set()

        for finlot_id in affected_finlot_ids:
            flot = finlot_map.get(finlot_id)
            finlot_qty = float(flot["quantity_produced"]) if flot else 1000.0
            total_qty_affected += finlot_qty

            affected_finlot_records.append({
                "recall_id": recall_id,
                "finished_lot_id": finlot_id,
                "qty_in_scope": finlot_qty,
            })

            # Check warehouse quarantine action
            if flot and float(flot.get("qty_remaining", 0)) > 0:
                q_qty = float(flot["qty_remaining"])
                flot["status"] = "QUARANTINED"
                recall_actions.append({
                    "action_id": IDGen.recall_action(action_counter),
                    "recall_id": recall_id,
                    "action_type": "QUARANTINE",
                    "target_entity_type": "FINISHED_LOT",
                    "target_entity_id": finlot_id,
                    "qty_affected": q_qty,
                    "qty_actioned": q_qty,
                    "status": "COMPLETED",
                    "notes": f"Warehouse inventory quarantined for {finlot_id}",
                })
                action_counter += 1

            # Traverse shipments and deliveries
            lot_shipments = shipments_by_finlot.get(finlot_id, [])
            for shp in lot_shipments:
                shp_delivs = deliveries_by_shipment.get(shp["shipment_id"], [])
                for deliv in shp_delivs:
                    affected_deliv_ids.append(deliv["delivery_id"])
                    affected_customer_ids.add(deliv["customer_id"])

                    affected_deliv_records.append({
                        "recall_id": recall_id,
                        "delivery_id": deliv["delivery_id"],
                        "qty_in_scope": float(deliv["qty_delivered"]),
                    })

        # Customer Notification Actions
        for cust_id in affected_customer_ids:
            recall_actions.append({
                "action_id": IDGen.recall_action(action_counter),
                "recall_id": recall_id,
                "action_type": "NOTIFY",
                "target_entity_type": "CUSTOMER",
                "target_entity_id": cust_id,
                "qty_affected": None,
                "qty_actioned": None,
                "status": "COMPLETED",
                "notes": f"Urgent safety recall notice sent to customer {cust_id}",
            })
            action_counter += 1

        # Product Recovery Actions (simulate 60% - 95% recovered)
        recovery_fraction = rng.uniform(0.60, 0.95)
        total_recovered = round(total_qty_affected * recovery_fraction, 2)
        recall_actions.append({
            "action_id": IDGen.recall_action(action_counter),
            "recall_id": recall_id,
            "action_type": "RECOVER",
            "target_entity_type": "FINISHED_LOT",
            "target_entity_id": f"MULTI-BATCH-{recall_id}",
            "qty_affected": total_qty_affected,
            "qty_actioned": total_recovered,
            "status": "COMPLETED",
            "notes": f"Physical recovery of returned lots across regional distribution hubs",
        })
        action_counter += 1

        is_closed = total_recovered >= total_qty_affected
        recall_cases.append({
            "recall_id": recall_id,
            "trigger_type": "RAW_LOT",
            "trigger_lot_id": trigger_lot_id,
            "reason": reason,
            "severity": severity,
            "initiated_by": "Dr. Aris Thorne (Chief Safety Officer)",
            "status": "CLOSED" if is_closed else "IN_PROGRESS",
            "total_qty_affected": total_qty_affected,
            "total_qty_recovered": total_recovered,
        })

    return recall_cases, affected_finlot_records, affected_deliv_records, recall_actions

