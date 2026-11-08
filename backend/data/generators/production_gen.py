import random
from datetime import date, timedelta
from typing import List, Dict, Any, Tuple
from data.generators.id_gen import IDGen

def generate_production_data(
    num_orders: int,
    target_finished_lots: int,
    products: List[Dict[str, Any]],
    bom_items: List[Dict[str, Any]],
    material_lots: List[Dict[str, Any]],
    rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates:
      1. production_orders
      2. production_consumptions
      3. finished_lots
      4. lot_genealogy
    """
    # Index BOM by product_id
    boms_by_product = {}
    for b in bom_items:
        boms_by_product.setdefault(b["product_id"], []).append(b)

    # Index material lots by material_type for quick lookup
    lots_by_type = {}
    for lot in material_lots:
        lots_by_type.setdefault(lot["material_type"], []).append(lot)

    production_orders = []
    consumptions = []
    finished_lots = []
    genealogy = []

    finlot_counter = 1
    base_date = date(2026, 2, 1)

    # Distribute target_finished_lots across num_orders
    # E.g. 8000 finished lots across 5000 orders => most have 1-2
    finlots_per_order = [1] * num_orders
    remaining_finlots = target_finished_lots - num_orders
    for idx in range(min(remaining_finlots, num_orders)):
        finlots_per_order[idx] += 1

    for order_idx in range(1, num_orders + 1):
        order_id = IDGen.production_order(order_idx)
        product = rng.choice(products)
        product_id = product["product_id"]
        product_boms = boms_by_product.get(product_id, [])

        planned_qty = float(round(rng.uniform(500.0, 3000.0), 2))
        actual_qty = float(round(planned_qty * rng.uniform(0.95, 1.05), 2))

        start_offset = rng.randint(0, 180)
        start_date = base_date + timedelta(days=start_offset)
        duration_days = rng.randint(1, 5)
        end_date = start_date + timedelta(days=duration_days)

        production_orders.append({
            "order_id": order_id,
            "product_id": product_id,
            "planned_qty": planned_qty,
            "actual_qty": actual_qty,
            "start_date": start_date,
            "end_date": end_date,
            "status": "COMPLETED",
            "location": f"PLANT-{rng.choice(['NORTH','SOUTH','EAST','WEST'])}-LINE-{rng.randint(1,8):02d}",
            "notes": "Standard automated batch execution",
        })

        # Consume material lots for each BOM item
        consumed_for_this_order = []
        for bom in product_boms:
            mat_type = bom["material_type"]
            needed_qty = bom["quantity_per_unit"] * actual_qty
            
            # Find available lots of this type
            type_lots = lots_by_type.get(mat_type, [])
            if not type_lots:
                # Fallback to any lot if specific type exhausted
                chosen_lot = rng.choice(material_lots)
            else:
                chosen_lot = rng.choice(type_lots)

            actual_consumed = min(needed_qty, float(chosen_lot["qty_remaining_kg"]))
            if actual_consumed <= 0:
                actual_consumed = min(needed_qty, float(chosen_lot["quantity_kg"]))
            
            # Update lot remaining qty
            chosen_lot["qty_remaining_kg"] = max(0.0, float(chosen_lot["qty_remaining_kg"]) - actual_consumed)
            if chosen_lot["qty_remaining_kg"] <= 0:
                chosen_lot["status"] = "CONSUMED"
            else:
                chosen_lot["status"] = "PARTIALLY_CONSUMED"

            consumptions.append({
                "order_id": order_id,
                "lot_id": chosen_lot["lot_id"],
                "qty_consumed": float(round(actual_consumed, 3)),
            })
            consumed_for_this_order.append((chosen_lot["lot_id"], actual_consumed))

        # Create finished lots for this order
        num_lots_for_order = finlots_per_order[order_idx - 1]
        lot_qty_share = actual_qty / num_lots_for_order

        for _ in range(num_lots_for_order):
            finlot_id = IDGen.finished_lot(finlot_counter)
            finlot_counter += 1

            fin_prod_date = end_date
            fin_expiry_date = fin_prod_date + timedelta(days=product["shelf_life_days"])

            finished_lots.append({
                "lot_id": finlot_id,
                "order_id": order_id,
                "product_id": product_id,
                "quantity_produced": float(round(lot_qty_share, 3)),
                "qty_remaining": float(round(lot_qty_share, 3)),
                "production_date": fin_prod_date,
                "expiry_date": fin_expiry_date,
                "status": "IN_WAREHOUSE",
                "storage_location": f"FINISHED-BAY-{rng.choice(['ALPHA','BETA','GAMMA'])}-{rng.randint(1,40):02d}",
            })

            # Record genealogy (FinishedLot <-> MaterialLot)
            for raw_lot_id, raw_consumed in consumed_for_this_order:
                portion_contributed = float(round(raw_consumed / num_lots_for_order, 3))
                genealogy.append({
                    "finished_lot_id": finlot_id,
                    "material_lot_id_ref": raw_lot_id,
                    "material_lot_id": raw_lot_id,
                    "qty_contributed": portion_contributed,
                })

    return production_orders, consumptions, finished_lots, genealogy

