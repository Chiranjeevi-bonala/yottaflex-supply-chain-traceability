import random
from typing import List, Dict, Any
from data.generators.id_gen import IDGen

CATEGORIES = ["CHEMICAL", "PACKAGING", "RAW_FOOD", "INGREDIENT", "ADDITIVE"]

SAMPLE_NAMES = [
    "BioNutra", "AgriPure", "ChemGlobal", "TerraFlavors", "ApexBotanicals",
    "SynthoChem", "SolariaNaturals", "HarvestYield", "VanguardOrganics", "NovaPack"
]
SAMPLE_SUFFIXES = ["Corp", "Inc", "LLC", "Ltd", "GmbH", "Enterprises", "International"]
SAMPLE_COUNTRIES = ["United States", "Germany", "Brazil", "India", "Netherlands", "Canada", "France", "Japan"]

def generate_suppliers(count: int, fake: Any, rng: random.Random) -> List[Dict[str, Any]]:
    suppliers = []
    for i in range(1, count + 1):
        supplier_id = IDGen.supplier(i)

        if fake:
            name = f"{fake.company()} {fake.company_suffix()}"
            country = fake.country()
            email = f"contact@{fake.domain_name()}"
            phone = fake.phone_number()
        else:
            name = f"{rng.choice(SAMPLE_NAMES)} {rng.choice(SAMPLE_SUFFIXES)} {i}"
            country = rng.choice(SAMPLE_COUNTRIES)
            email = f"procurement@supp-{i:04d}.example.com"
            phone = f"+1-{rng.randint(200,999)}-555-{rng.randint(1000,9999)}"

        suppliers.append({
            "supplier_id": supplier_id,
            "name": name,
            "country": country,
            "category": rng.choice(CATEGORIES),
            "contact_email": email,
            "contact_phone": phone,
            "is_active": rng.random() > 0.05,
            "reliability_score": round(rng.uniform(0.70, 0.99), 2),
        })
    return suppliers
