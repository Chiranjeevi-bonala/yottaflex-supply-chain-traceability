from dataclasses import dataclass
from typing import Dict

FIXED_SEED: int = 20261022

@dataclass
class DataScale:
    num_suppliers: int
    num_material_lots: int
    num_products: int
    num_production_orders: int
    num_finished_lots: int
    num_customers: int
    num_deliveries: int

SCALE_CONFIGS: Dict[str, DataScale] = {
    "starter": DataScale(
        num_suppliers=20,
        num_material_lots=150,
        num_products=10,
        num_production_orders=50,
        num_finished_lots=80,
        num_customers=30,
        num_deliveries=200,
    ),
    "medium": DataScale(
        num_suppliers=100,
        num_material_lots=2000,
        num_products=25,
        num_production_orders=1000,
        num_finished_lots=1600,
        num_customers=200,
        num_deliveries=4000,
    ),
    "full": DataScale(
        num_suppliers=500,
        num_material_lots=10000,
        num_products=50,
        num_production_orders=5000,
        num_finished_lots=8000,
        num_customers=1000,
        num_deliveries=20000,
    ),
}

def get_scale(scale_name: str = "full") -> DataScale:
    if scale_name not in SCALE_CONFIGS:
        raise ValueError(f"Unknown scale '{scale_name}'. Allowed: {list(SCALE_CONFIGS.keys())}")
    return SCALE_CONFIGS[scale_name]

