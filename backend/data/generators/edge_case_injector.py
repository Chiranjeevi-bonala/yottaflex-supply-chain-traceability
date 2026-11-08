import random
from typing import List, Dict, Any, Tuple
from data.generators.id_gen import IDGen

def inject_edge_cases(
    genealogy: List[Dict[str, Any]],
    finished_lots: List[Dict[str, Any]],
    shipments: List[Dict[str, Any]],
    deliveries: List[Dict[str, Any]],
    recall_cases: List[Dict[str, Any]],
    recall_actions: List[Dict[str, Any]],
    affected_deliveries: List[Dict[str, Any]],
    customers: List[Dict[str, Any]],
    rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Injects all 4 mandatory edge cases with isolated ground-truth labels:
      1. EC-01: Finished lot references missing input lot
      2. EC-02: Delivered quantity exceeds produced quantity
      3. EC-03: Recall misses a downstream customer
      4. EC-04: Recalled inventory remains available for sale
    Returns:
      (exception_records, ground_truth_entries)
    """
    exception_records = []
    ground_truth_entries = []

    # -------------------------------------------------------------
    # EC-01: Finished lot references missing input lot
    # -------------------------------------------------------------
    target_finlot = finished_lots[10]
    ghost_raw_lot_id = "RAWLOT-SUP-999999-2026-999999"
    genealogy.append({
        "finished_lot_id": target_finlot["lot_id"],
        "material_lot_id_ref": ghost_raw_lot_id,
        "material_lot_id": None,  # Missing foreign key reference
        "qty_contributed": 150.0,
    })

    ec01_gt = {
        "issue_type": "MISSING_INPUT_LOT",
        "finished_lot_id": target_finlot["lot_id"],
        "missing_material_lot_id": ghost_raw_lot_id,
        "expected_decision": "Quarantine finished lot immediately; conduct BOM verification audit",
        "operational_impact": "Loss of upstream traceability; potential unverified allergen or contaminant",
        "is_ground_truth": True,
    }
    exception_records.append({
        "exception_id": IDGen.exception_record(1),
        "issue_type": "MISSING_INPUT_LOT",
        "entity_type": "FINISHED_LOT",
        "entity_id": target_finlot["lot_id"],
        "detection_status": "DETECTED",
        "impact_description": ec01_gt["operational_impact"],
        "expected_decision": ec01_gt["expected_decision"],
        "ground_truth_label": ec01_gt,
    })
    ground_truth_entries.append(ec01_gt)

    # -------------------------------------------------------------
    # EC-02: Delivered quantity exceeds produced quantity
    # -------------------------------------------------------------
    target_overrun_finlot = finished_lots[25]
    prod_qty = float(target_overrun_finlot["quantity_produced"])
    overrun_amount = 500.0
    
    # Find or attach a delivery on this lot
    matching_shipments = [s for s in shipments if s["finished_lot_id"] == target_overrun_finlot["lot_id"]]
    if matching_shipments:
        target_shp = matching_shipments[0]
        # Inject an excessive delivery
        inflated_deliv_qty = prod_qty + overrun_amount
        deliveries.append({
            "delivery_id": "DEL-OVERRUN-000001",
            "shipment_id": target_shp["shipment_id"],
            "customer_id": customers[0]["customer_id"],
            "qty_delivered": inflated_deliv_qty,
            "delivery_date": target_shp["actual_delivery_date"],
            "status": "DELIVERED",
            "notes": "System anomaly: duplicate bill of lading entry created overrun",
        })

    ec02_gt = {
        "issue_type": "DELIVERY_OVERRUN",
        "finished_lot_id": target_overrun_finlot["lot_id"],
        "produced_quantity": prod_qty,
        "overrun_quantity": overrun_amount,
        "expected_decision": "Halt matching shipment settlement; reconcile warehouse physical stock against ERP",
        "operational_impact": "Inventory phantom stock; potential unrecorded parallel production or billing error",
        "is_ground_truth": True,
    }
    exception_records.append({
        "exception_id": IDGen.exception_record(2),
        "issue_type": "DELIVERY_OVERRUN",
        "entity_type": "FINISHED_LOT",
        "entity_id": target_overrun_finlot["lot_id"],
        "detection_status": "DETECTED",
        "impact_description": ec02_gt["operational_impact"],
        "expected_decision": ec02_gt["expected_decision"],
        "ground_truth_label": ec02_gt,
    })
    ground_truth_entries.append(ec02_gt)

    # -------------------------------------------------------------
    # EC-03: Recall misses a downstream customer
    # -------------------------------------------------------------
    if recall_cases and affected_deliveries:
        target_recall = recall_cases[0]
        # Find deliveries in this recall
        rec_deliv_ids = [ad["delivery_id"] for ad in affected_deliveries if ad["recall_id"] == target_recall["recall_id"]]
        matching_delivs = [d for d in deliveries if d["delivery_id"] in rec_deliv_ids]
        
        if matching_delivs:
            missed_deliv = matching_delivs[0]
            missed_cust_id = missed_deliv["customer_id"]
            
            # Intentionally remove any NOTIFY action for this customer in this recall
            idx_to_remove = []
            for idx, act in enumerate(recall_actions):
                if act["recall_id"] == target_recall["recall_id"] and act["action_type"] == "NOTIFY" and act["target_entity_id"] == missed_cust_id:
                    idx_to_remove.append(idx)
            for idx in reversed(idx_to_remove):
                recall_actions.pop(idx)

            ec03_gt = {
                "issue_type": "MISSED_CUSTOMER",
                "recall_id": target_recall["recall_id"],
                "customer_id": missed_cust_id,
                "delivery_id": missed_deliv["delivery_id"],
                "expected_decision": "Dispatch immediate priority recall telegram and dispatch field rep",
                "operational_impact": "End consumer exposure to tainted goods; regulatory fine risk",
                "is_ground_truth": True,
            }
            exception_records.append({
                "exception_id": IDGen.exception_record(3),
                "issue_type": "MISSED_CUSTOMER",
                "entity_type": "CUSTOMER",
                "entity_id": missed_cust_id,
                "detection_status": "DETECTED",
                "impact_description": ec03_gt["operational_impact"],
                "expected_decision": ec03_gt["expected_decision"],
                "ground_truth_label": ec03_gt,
            })
            ground_truth_entries.append(ec03_gt)

    # -------------------------------------------------------------
    # EC-04: Recalled inventory remains available for sale
    # -------------------------------------------------------------
    if recall_cases:
        target_recall = recall_cases[0]
        # Identify finished lots associated with this recall via existing QUARANTINE actions
        associated_lot_ids = [a["target_entity_id"] for a in recall_actions if a["recall_id"] == target_recall["recall_id"] and a["action_type"] == "QUARANTINE"]
        if not associated_lot_ids:
            raise ValueError("No finished lot associated with the selected recall for EC-04 injection.")
        # Choose the first associated finished lot
        finlot_id = associated_lot_ids[0]
        # Locate the finished lot object in finished_lots list
        leaked_finlot = next(fl for fl in finished_lots if fl["lot_id"] == finlot_id)
        # Set required status and quantity
        leaked_finlot["status"] = "IN_WAREHOUSE"
        leaked_finlot["qty_remaining"] = 350.0

        # Remove the matching QUARANTINE action
        recall_actions[:] = [
            a for a in recall_actions
            if not (a["recall_id"] == target_recall["recall_id"] and a["target_entity_id"] == finlot_id and a["action_type"] == "QUARANTINE")
        ]

        ec04_gt = {
            "issue_type": "INVENTORY_NOT_QUARANTINED",
            "recall_id": target_recall["recall_id"],
            "finished_lot_id": finlot_id,
            "available_quantity": 350.0,
            "expected_decision": "Lock warehouse bin immediately in WMS; cancel all pending pick waves",
            "operational_impact": "Contaminated units risk being picked and shipped during active recall",
            "is_ground_truth": True,
        }
        exception_records.append({
            "exception_id": IDGen.exception_record(4),
            "issue_type": "INVENTORY_NOT_QUARANTINED",
            "entity_type": "FINISHED_LOT",
            "entity_id": finlot_id,
            "detection_status": "DETECTED",
            "impact_description": ec04_gt["operational_impact"],
            "expected_decision": ec04_gt["expected_decision"],
            "ground_truth_label": ec04_gt,
        })
        ground_truth_entries.append(ec04_gt)

    return exception_records, ground_truth_entries

