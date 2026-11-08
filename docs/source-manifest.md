# Source Data Manifest & Lawful Use Declaration

## 1. Data Provenance & Lawful Use
All data utilized in this system is **100% synthetically generated** using deterministic algorithmic generators:
- **Core Generator**: Python `faker` library paired with Python's built-in `random.Random` initialized with fixed seed `20261022`.
- **No Third-Party Personal Data**: No real customer names, confidential email addresses, proprietary supplier details, or real lot numbers are stored or scraped.
- **Lawful Compliance**: No external web crawling, anti-bot bypass, or unauthorized data ingestion was performed.

## 2. Seed Reproducibility
- **Fixed Seed**: `20261022`
- **Volume Targets**:
  - Suppliers: `500`
  - Raw Material Lots: `10,000`
  - Production Orders: `5,000`
  - Finished Lots: `8,000`
  - Deliveries: `20,000`
- **Reproducibility Verification**:
  Running the generator twice with seed `20261022` produces bit-for-bit identical row counts across all 16 tables and matching MD5 checksums.

## 3. Transformation & Logic Rules
1. Master entities (`Supplier`, `Product`, `BOM`) generated first.
2. Raw material lots allocated to suppliers with deterministic IDs (`RAWLOT-{supplier-id}-2026-000001`).
3. Production orders consume raw lots according to product BOM requirements.
4. Finished lots allocated to shipments, ensuring shipped volume does not exceed remaining volume.
5. Shipments split into customer deliveries, enforcing delivered volume <= shipped volume.
6. Recall scope generated strictly by traversing genealogy relations downstream.

