import os
import sys
import random
import hashlib
import argparse
from typing import Dict, List, Any

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from data.generators.config import FIXED_SEED, get_scale
from data.generators.supplier_gen import generate_suppliers
from data.generators.product_bom_gen import generate_products_and_boms
from data.generators.material_lot_gen import generate_material_lots
from data.generators.production_gen import generate_production_data
from data.generators.distribution_gen import generate_customers, generate_distribution_data
from data.generators.recall_gen import generate_recalls
from data.generators.edge_case_injector import inject_edge_cases

from data.exports.csv_exporter import export_all_to_csv
from data.exports.json_exporter import export_all_to_json
from data.exports.sql_exporter import export_to_sql_seed
from data.exports.ground_truth_exporter import export_ground_truth

def run_pipeline(scale_name: str = "full", seed: int = FIXED_SEED, export: bool = True):
    print("=" * 70)
    print(f"YottaFlex Supply Chain Traceability - Data Generation Pipeline")
    print(f"Scale: {scale_name.upper()} | Fixed Seed: {seed}")
    print("=" * 70)

    # 1. Deterministic Seeds
    rng = random.Random(seed)
    fake = None
    try:
        from faker import Faker
        Faker.seed(seed)
        fake = Faker()
    except ImportError:
        pass

    scale = get_scale(scale_name)

    # 2. Master Data Generation
    print("\n[1/6] Generating Master Data (Suppliers, Products, BOMs)...")
    suppliers = generate_suppliers(scale.num_suppliers, fake, rng)
    products, bom_items = generate_products_and_boms(scale.num_products, rng)
    print(f"  Suppliers: {len(suppliers)}")
    print(f"  Products: {len(products)} | BOM Items: {len(bom_items)}")

    # 3. Raw Material Lots
    print("\n[2/6] Generating Raw Material Lots...")
    material_lots = generate_material_lots(scale.num_material_lots, suppliers, rng)
    print(f"  Material Lots: {len(material_lots)}")

    # 4. Production & Genealogy
    print("\n[3/6] Generating Production Runs & Material Consumption Genealogy...")
    orders, consumptions, finished_lots, genealogy = generate_production_data(
        num_orders=scale.num_production_orders,
        target_finished_lots=scale.num_finished_lots,
        products=products,
        bom_items=bom_items,
        material_lots=material_lots,
        rng=rng
    )
    print(f"  Production Orders: {len(orders)}")
    print(f"  Material Consumptions: {len(consumptions)}")
    print(f"  Finished Lots: {len(finished_lots)}")
    print(f"  Lot Genealogy Links: {len(genealogy)}")

    # 5. Distribution (Customers, Shipments, Deliveries)
    print("\n[4/6] Generating Customers, Shipments & Deliveries...")
    customers = generate_customers(scale.num_customers, fake, rng)
    shipments, deliveries = generate_distribution_data(
        num_deliveries=scale.num_deliveries,
        finished_lots=finished_lots,
        customers=customers,
        rng=rng
    )
    print(f"  Customers: {len(customers)}")
    print(f"  Shipments: {len(shipments)}")
    print(f"  Deliveries: {len(deliveries)}")

    # 6. Recalls & Downstream Scope Traversal
    print("\n[5/6] Simulating Recalls and Downstream Scope Traversal...")
    num_recalls = 10 if scale_name == "full" else 2
    recalls, aff_finlots, aff_delivs, recall_actions = generate_recalls(
        num_recalls=num_recalls,
        material_lots=material_lots,
        genealogy=genealogy,
        shipments=shipments,
        deliveries=deliveries,
        finished_lots=finished_lots,
        rng=rng
    )
    print(f"  Recall Cases: {len(recalls)}")
    print(f"  Affected Finished Lots: {len(aff_finlots)}")
    print(f"  Affected Deliveries: {len(aff_delivs)}")
    print(f"  Recall Actions (Notify/Quarantine/Recover): {len(recall_actions)}")

    # 7. Edge Case Injection (EC-01 .. EC-04)
    print("\n[6/6] Injecting 4 Mandatory Edge Cases & Ground-Truth Labels...")
    exceptions, ground_truth = inject_edge_cases(
        genealogy=genealogy,
        finished_lots=finished_lots,
        shipments=shipments,
        deliveries=deliveries,
        recall_cases=recalls,
        recall_actions=recall_actions,
        affected_deliveries=aff_delivs,
        customers=customers,
        rng=rng
    )
    print(f"  Exceptions Injected: {len(exceptions)}")
    print(f"  Ground Truth Records: {len(ground_truth)}")

    all_data = {
        "suppliers": suppliers,
        "products": products,
        "bom_items": bom_items,
        "material_lots": material_lots,
        "production_orders": orders,
        "production_consumptions": consumptions,
        "finished_lots": finished_lots,
        "lot_genealogy": genealogy,
        "customers": customers,
        "shipments": shipments,
        "deliveries": deliveries,
        "recall_cases": recalls,
        "recall_affected_finished_lots": aff_finlots,
        "recall_affected_deliveries": aff_delivs,
        "recall_actions": recall_actions,
        "exception_records": exceptions,
    }

    # 8. Checksums
    checksum_str = ""
    for k in sorted(all_data.keys()):
        checksum_str += f"{k}:{len(all_data[k])};"
    dataset_md5 = hashlib.md5(checksum_str.encode()).hexdigest()
    print("\n" + "=" * 70)
    print(f"DATASET GENERATION COMPLETE | Checksum (MD5): {dataset_md5}")
    print("=" * 70)

    # 9. Exports
    if export:
        base_export_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "exports"))
        print(f"\nWriting Exports to: {base_export_dir}")
        export_all_to_csv(all_data, os.path.join(base_export_dir, "csv"))
        export_all_to_json(all_data, os.path.join(base_export_dir, "json"))
        export_to_sql_seed(all_data, os.path.join(base_export_dir, "sql", "seed.sql"))
        export_ground_truth(ground_truth, os.path.join(base_export_dir, "ground_truth"))

    return all_data, dataset_md5

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supply Chain Traceability Synthetic Data Pipeline")
    parser.add_argument("--scale", choices=["starter", "medium", "full"], default="starter", help="Dataset scale")
    parser.add_argument("--seed", type=int, default=FIXED_SEED, help="Seed for reproducibility")
    parser.add_argument("--no-export", action="store_true", help="Skip writing export files")
    args = parser.parse_args()

    run_pipeline(scale_name=args.scale, seed=args.seed, export=not args.no_export)
