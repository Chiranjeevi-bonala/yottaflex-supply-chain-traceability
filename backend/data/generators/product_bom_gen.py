import random
from typing import List, Dict, Any, Tuple
from data.generators.id_gen import IDGen

# Material types grouped by category
MATERIAL_TYPES_BY_CAT = {
    "INGREDIENT": ["Wheat Flour Organic", "Cane Sugar Extra Fine", "Soy Protein Isolate", "Cocoa Powder Dutch", "Corn Starch"],
    "ADDITIVE": ["Citric Acid Anhydrous", "Ascorbic Acid Grade A", "Natural Vanilla Extract", "Lecithin Emulsifier", "Sodium Benzoate"],
    "RAW_FOOD": ["Whole Milk Fresh", "Filtered Water Grade 1", "Egg White Pasteurized", "Vegetable Oil Pure", "Almond Paste Raw"],
    "CHEMICAL": ["Food Grade Nitrogen", "Ethanol 96 Pct Food", "Potassium Hydroxide", "Lactic Acid Purified", "Calcium Chloride"],
    "PACKAGING": ["PET Bottle 500ml", "Carton Box 12-Pack", "Aseptic Tetra Pouch 250ml", "Aluminum Foil Seal", "Corrugated Shipper Outer"]
}

PRODUCT_TEMPLATES = [
    ("Organic Chocolate Protein Shake 500ml", "BEVERAGE", "UNIT", 180, ["Milk", "Cocoa", "Sugar", "Soy", "Bottle"]),
    ("Energy Bar High Fiber Almond 60g", "SNACK", "UNIT", 365, ["Almond", "Flour", "Sugar", "Vanilla", "Foil"]),
    ("Citrus Electrolyte Drink 250ml", "BEVERAGE", "UNIT", 270, ["Water", "Citric", "Sugar", "Ascorbic", "Pouch"]),
    ("Artisan Bakery Premix 5kg", "FOOD_SERVICE", "KG", 120, ["Flour", "Sugar", "Corn Starch", "Lecithin", "Box"]),
    ("Pure Soy Lecithin Emulsion 1L", "INGREDIENTS", "LITER", 360, ["Lecithin", "Ethanol", "Water", "Bottle", "Box"]),
]

def generate_products_and_boms(num_products: int, rng: random.Random) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    products = []
    bom_items = []
    bom_counter = 1

    all_raw_materials = []
    for m_list in MATERIAL_TYPES_BY_CAT.values():
        all_raw_materials.extend(m_list)

    for i in range(1, num_products + 1):
        product_id = IDGen.product(i)
        template_idx = (i - 1) % len(PRODUCT_TEMPLATES)
        tmpl_name, tmpl_cat, tmpl_uom, tmpl_shelf, _ = PRODUCT_TEMPLATES[template_idx]
        name = f"{tmpl_name} - Variant {i}"
        sku = f"SKU-{tmpl_cat[:3]}-{i:04d}"

        products.append({
            "product_id": product_id,
            "name": name,
            "sku": sku,
            "category": tmpl_cat,
            "uom": tmpl_uom,
            "shelf_life_days": tmpl_shelf,
            "is_active": True,
        })

        # Generate 3-5 BOM items per product
        num_ingredients = rng.randint(3, 5)
        selected_materials = rng.sample(all_raw_materials, num_ingredients)
        for mat in selected_materials:
            bom_items.append({
                "bom_id": IDGen.bom(bom_counter),
                "product_id": product_id,
                "material_type": mat,
                "quantity_per_unit": round(rng.uniform(0.05, 0.40), 4),
                "unit": "KG",
                "is_active": True,
            })
            bom_counter += 1

    return products, bom_items

