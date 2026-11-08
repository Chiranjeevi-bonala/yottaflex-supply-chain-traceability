import random
from datetime import date, timedelta
from typing import List, Dict, Any
from data.generators.id_gen import IDGen
from data.generators.product_bom_gen import MATERIAL_TYPES_BY_CAT

def generate_material_lots(
    num_lots: int,
    suppliers: List[Dict[str, Any]],
    rng: random.Random
) -> List[Dict[str, Any]]:
    material_lots = []
    
    # Map suppliers by category for realistic material types
    supp_by_cat = {}
    for s in suppliers:
        supp_by_cat.setdefault(s["category"], []).append(s)

    base_date = date(2026, 1, 1)

    for i in range(1, num_lots + 1):
        # Pick category, then supplier
        cat = rng.choice(list(MATERIAL_TYPES_BY_CAT.keys()))
        sup_pool = supp_by_cat.get(cat, suppliers)
        supplier = rng.choice(sup_pool)
        supplier_id = supplier["supplier_id"]

        lot_id = IDGen.material_lot(supplier_id, i)
        material_type = rng.choice(MATERIAL_TYPES_BY_CAT[cat])
        
        receipt_offset = rng.randint(0, 150)
        receipt_date = base_date + timedelta(days=receipt_offset)
        shelf_life_days = rng.randint(180, 540)
        expiry_date = receipt_date + timedelta(days=shelf_life_days)

        qty = float(round(rng.uniform(1000.0, 8000.0), 3))

        material_lots.append({
            "lot_id": lot_id,
            "supplier_id": supplier_id,
            "material_type": material_type,
            "quantity_kg": qty,
            "qty_remaining_kg": qty,
            "unit": "KG",
            "receipt_date": receipt_date,
            "expiry_date": expiry_date,
            "status": "IN_STOCK",
            "storage_location": f"WH-ZONE-{rng.choice(['A','B','C','D'])}-{rng.randint(1,50):02d}",
            "is_contaminated": False,
        })

    return material_lots

