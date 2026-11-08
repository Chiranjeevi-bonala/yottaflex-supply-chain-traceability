import random
from datetime import date, timedelta
from typing import List, Dict, Any, Tuple
from data.generators.id_gen import IDGen

CARRIERS = ["FedEx Freight", "DHL Supply Chain", "Kuehne+Nagel", "Maersk Logistics", "DB Schenker", "XPO Logistics"]

SAMPLE_CUSTOMERS = [
    "Target Retail Network", "Costco Wholesale Hub", "Kroger Central Distribution",
    "Walmart Global Sourcing", "Sysco Foodservice Operations", "Whole Foods Regional Depot",
    "Albertsons Distribution Alliance", "Ahold Delhaize Logistics"
]

def generate_customers(num_customers: int, fake: Any, rng: random.Random) -> List[Dict[str, Any]]:
    customers = []
    tiers = ["GOLD", "SILVER", "BRONZE", "STANDARD"]
    tier_weights = [0.15, 0.25, 0.35, 0.25]

    for i in range(1, num_customers + 1):
        cust_id = IDGen.customer(i)
        
        if fake:
            name = f"{fake.company()} {fake.company_suffix()}"
            country = fake.country()
            email = f"procurement@{fake.domain_name()}"
            phone = fake.phone_number()
        else:
            base_name = SAMPLE_CUSTOMERS[(i - 1) % len(SAMPLE_CUSTOMERS)]
            name = f"{base_name} - Facility {i:03d}"
            country = "United States" if i % 2 == 0 else "Germany"
            email = f"receiving@client-{i:04d}.example.com"
            phone = f"+1-{rng.randint(200,999)}-555-{rng.randint(1000,9999)}"

        customers.append({
            "customer_id": cust_id,
            "name": name,
            "country": country,
            "region": rng.choice(["North America", "EMEA", "APAC", "LATAM"]),
            "contact_email": email,
            "contact_phone": phone,
            "tier": rng.choices(tiers, weights=tier_weights, k=1)[0],
            "is_active": True,
        })
    return customers

def generate_distribution_data(
    num_deliveries: int,
    finished_lots: List[Dict[str, Any]],
    customers: List[Dict[str, Any]],
    rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    shipments = []
    deliveries = []

    shipment_counter = 1
    delivery_counter = 1

    est_shipments_needed = int(num_deliveries * 0.75)
    finlot_pool = [lot for lot in finished_lots if float(lot["qty_remaining"]) > 0]
    
    while len(shipments) < est_shipments_needed and finlot_pool:
        lot = rng.choice(finlot_pool)
        available_qty = float(lot["qty_remaining"])
        if available_qty <= 1.0:
            finlot_pool.remove(lot)
            continue

        if available_qty < 100 or rng.random() > 0.7:
            ship_qty = available_qty
        else:
            ship_qty = float(round(available_qty * rng.uniform(0.3, 0.8), 2))

        lot["qty_remaining"] = max(0.0, available_qty - ship_qty)
        if lot["qty_remaining"] <= 0.01:
            lot["status"] = "SHIPPED"
            if lot in finlot_pool:
                finlot_pool.remove(lot)
        else:
            lot["status"] = "PARTIALLY_SHIPPED"

        prod_date = lot["production_date"]
        ship_offset = rng.randint(2, 20)
        ship_date = prod_date + timedelta(days=ship_offset)
        transit_days = rng.randint(1, 7)
        exp_deliv = ship_date + timedelta(days=transit_days)

        shipment_id = IDGen.shipment(shipment_counter)
        shipment_counter += 1

        shipments.append({
            "shipment_id": shipment_id,
            "finished_lot_id": lot["lot_id"],
            "carrier": rng.choice(CARRIERS),
            "ship_date": ship_date,
            "expected_delivery_date": exp_deliv,
            "actual_delivery_date": exp_deliv,
            "status": "DELIVERED",
            "qty_shipped": float(round(ship_qty, 3)),
            "destination_region": rng.choice(["North America", "EMEA", "APAC", "LATAM"]),
            "tracking_number": f"TRK-{rng.randint(10000000, 99999999)}",
        })

    deliveries_per_shipment = [1] * len(shipments)
    extra_deliveries = num_deliveries - len(shipments)
    if extra_deliveries > 0:
        for idx in range(extra_deliveries):
            target_idx = idx % len(shipments)
            deliveries_per_shipment[target_idx] += 1

    for s_idx, shipment in enumerate(shipments):
        count_for_this = deliveries_per_shipment[s_idx]
        total_ship_qty = float(shipment["qty_shipped"])
        
        shares = [rng.uniform(1.0, 3.0) for _ in range(count_for_this)]
        sum_shares = sum(shares)
        
        allocated_so_far = 0.0
        for d_i in range(count_for_this):
            if d_i == count_for_this - 1:
                deliv_qty = float(round(total_ship_qty - allocated_so_far, 3))
            else:
                deliv_qty = float(round(total_ship_qty * (shares[d_i] / sum_shares), 3))
                allocated_so_far += deliv_qty

            deliv_qty = max(0.01, deliv_qty)
            customer = rng.choice(customers)
            deliv_id = IDGen.delivery(delivery_counter)
            delivery_counter += 1

            deliv_date = shipment["actual_delivery_date"]
            deliveries.append({
                "delivery_id": deliv_id,
                "shipment_id": shipment["shipment_id"],
                "customer_id": customer["customer_id"],
                "qty_delivered": deliv_qty,
                "delivery_date": deliv_date,
                "status": "DELIVERED",
                "notes": f"Proof of Delivery signed by {customer['name'][:20]}",
            })

    return shipments, deliveries
