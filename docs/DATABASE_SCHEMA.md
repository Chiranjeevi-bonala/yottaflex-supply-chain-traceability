# Database Schema Specification: YottaFlex SCM

**Project:** YottaFlex Supply Chain Traceability and Recall Management System  
**Seed Reference:** `20261022`  
**Revision:** `001_initial` (Alembic)

---

## 1. Schema Architecture Overview

The YottaFlex relational schema is designed around high-throughput batch operations, strict referential integrity, and graph-like multi-echelon traversal. The architecture is deployed to PostgreSQL 15+ in production and supports SQLite 3 (with `StaticPool`) for zero-overhead integration testing.

The 17 relational tables are organized into four logical tiers:
1. **Master Upstream**: `suppliers`, `products`, `bom_items`, `material_lots`.
2. **Manufacturing**: `production_orders`, `production_consumptions`, `finished_lots`, `lot_genealogy`.
3. **Logistics & Distribution**: `shipments`, `customers`, `deliveries`.
4. **Safety & Audit**: `recall_cases`, `recall_actions`, `recall_affected_finished_lots`, `recall_affected_deliveries`, `exception_records`.

---

## 2. Table Schemas, Constraints & Foreign Keys

### 2.1 Upstream Entities

#### Table: `suppliers`
- **Primary Key:** `supplier_id VARCHAR(20)`
- **Constraints:**
  - `CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0)`
  - `CHECK (category IN ('INGREDIENT', 'CHEMICAL', 'PACKAGING'))`
- **Indexes:**
  - `idx_suppliers_category` on `category`
  - `idx_suppliers_country` on `country`

#### Table: `products`
- **Primary Key:** `product_id VARCHAR(20)`
- **Constraints:**
  - `UNIQUE (sku)`
  - `CHECK (shelf_life_days > 0)`
- **Indexes:**
  - `idx_products_sku` on `sku`
  - `idx_products_category` on `category`

#### Table: `bom_items`
- **Primary Key:** `bom_id VARCHAR(20)`
- **Foreign Keys:**
  - `product_id` -> `products(product_id)` ON DELETE RESTRICT
- **Constraints:**
  - `CHECK (quantity_per_unit > 0)`
- **Indexes:**
  - `idx_bom_product_id` on `product_id`

#### Table: `material_lots`
- **Primary Key:** `lot_id VARCHAR(60)`
- **Foreign Keys:**
  - `supplier_id` -> `suppliers(supplier_id)` ON DELETE RESTRICT
- **Constraints:**
  - `CHECK (quantity_kg > 0)`
  - `CHECK (qty_remaining_kg >= 0)`
  - `CHECK (qty_remaining_kg <= quantity_kg)`
  - `CHECK (expiry_date >= receipt_date)`
  - `CHECK (status IN ('RECEIVED', 'IN_USE', 'EXHAUSTED', 'QUARANTINED'))`
- **Indexes:**
  - `idx_material_lots_supplier` on `supplier_id`
  - `idx_material_lots_status` on `status`
  - `idx_material_lots_type` on `material_type`

---

### 2.2 Manufacturing & Genealogy Entities

#### Table: `production_orders`
- **Primary Key:** `order_id VARCHAR(20)`
- **Foreign Keys:**
  - `product_id` -> `products(product_id)` ON DELETE RESTRICT
- **Constraints:**
  - `CHECK (planned_qty > 0)`
  - `CHECK (actual_qty IS NULL OR actual_qty >= 0)`
  - `CHECK (status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))`
- **Indexes:**
  - `idx_orders_product` on `product_id`
  - `idx_orders_status` on `status`

#### Table: `production_consumptions`
- **Primary Key:** `consumption_id VARCHAR(20)`
- **Foreign Keys:**
  - `order_id` -> `production_orders(order_id)` ON DELETE CASCADE
  - `lot_id` -> `material_lots(lot_id)` ON DELETE RESTRICT
- **Constraints:**
  - `CHECK (qty_consumed > 0)`
- **Indexes:**
  - `idx_consumptions_order` on `order_id`
  - `idx_consumptions_lot` on `lot_id`

#### Table: `finished_lots`
- **Primary Key:** `lot_id VARCHAR(30)`
- **Foreign Keys:**
  - `order_id` -> `production_orders(order_id)` ON DELETE RESTRICT
  - `product_id` -> `products(product_id)` ON DELETE RESTRICT
- **Constraints:**
  - `CHECK (quantity_produced > 0)`
  - `CHECK (qty_remaining >= 0)`
  - `CHECK (qty_remaining <= quantity_produced)`
  - `CHECK (expiry_date >= production_date)`
  - `CHECK (status IN ('IN_WAREHOUSE', 'RELEASED', 'QUARANTINED', 'RECALLED'))`
- **Indexes:**
  - `idx_finished_lots_order` on `order_id`
  - `idx_finished_lots_product` on `product_id`
  - `idx_finished_lots_status` on `status`

#### Table: `lot_genealogy`
- **Primary Key:** `genealogy_id INTEGER AUTO_INCREMENT`
- **Foreign Keys:**
  - `finished_lot_id` -> `finished_lots(lot_id)` ON DELETE CASCADE
  - `material_lot_id` -> `material_lots(lot_id)` ON DELETE SET NULL
- **Constraints:**
  - `CHECK (qty_contributed > 0)`
- **Indexes:**
  - `idx_genealogy_finlot` on `finished_lot_id`
  - `idx_genealogy_matlot` on `material_lot_id`
  - `idx_genealogy_ref` on `material_lot_id_ref`

---

### 2.3 Logistics & Delivery Entities

#### Table: `shipments`
- **Primary Key:** `shipment_id VARCHAR(20)`
- **Foreign Keys:**
  - `finished_lot_id` -> `finished_lots(lot_id)` ON DELETE RESTRICT
- **Constraints:**
  - `CHECK (qty_shipped > 0)`
  - `CHECK (expected_delivery_date >= ship_date)`
  - `CHECK (status IN ('CREATED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED'))`
- **Indexes:**
  - `idx_shipments_finlot` on `finished_lot_id`
  - `idx_shipments_carrier` on `carrier`

#### Table: `customers`
- **Primary Key:** `customer_id VARCHAR(20)`
- **Constraints:**
  - `CHECK (tier IN ('PLATINUM', 'GOLD', 'SILVER', 'STANDARD'))`
- **Indexes:**
  - `idx_customers_tier` on `tier`
  - `idx_customers_country` on `country`

#### Table: `deliveries`
- **Primary Key:** `delivery_id VARCHAR(20)`
- **Foreign Keys:**
  - `shipment_id` -> `shipments(shipment_id)` ON DELETE RESTRICT
  - `customer_id` -> `customers(customer_id)` ON DELETE RESTRICT
- **Constraints:**
  - `CHECK (qty_delivered > 0)`
  - `CHECK (status IN ('DELIVERED', 'REJECTED', 'RETURNED'))`
- **Indexes:**
  - `idx_deliveries_shipment` on `shipment_id`
  - `idx_deliveries_customer` on `customer_id`

---

### 2.4 Safety & Recall Entities

#### Table: `recall_cases`
- **Primary Key:** `recall_id VARCHAR(20)`
- **Constraints:**
  - `CHECK (trigger_type IN ('RAW_LOT', 'FINISHED_LOT'))`
  - `CHECK (severity IN ('CLASS_I', 'CLASS_II', 'CLASS_III'))`
  - `CHECK (status IN ('OPEN', 'IN_PROGRESS', 'CLOSED'))`
  - `CHECK (total_qty_recovered >= 0)`
- **Indexes:**
  - `idx_recalls_status` on `status`
  - `idx_recalls_trigger` on `trigger_lot_id`

#### Table: `recall_actions`
- **Primary Key:** `action_id VARCHAR(20)`
- **Foreign Keys:**
  - `recall_id` -> `recall_cases(recall_id)` ON DELETE CASCADE
- **Constraints:**
  - `CHECK (action_type IN ('NOTIFY', 'QUARANTINE', 'RECOVER'))`
  - `CHECK (target_entity_type IN ('CUSTOMER', 'FINISHED_LOT', 'SHIPMENT', 'DELIVERY'))`
- **Indexes:**
  - `idx_actions_recall` on `recall_id`
  - `idx_actions_type` on `action_type`

#### Table: `recall_affected_finished_lots`
- **Primary Key:** `id INTEGER AUTO_INCREMENT`
- **Foreign Keys:**
  - `recall_id` -> `recall_cases(recall_id)` ON DELETE CASCADE
  - `finished_lot_id` -> `finished_lots(lot_id)` ON DELETE CASCADE
- **Constraints:**
  - `CHECK (qty_in_scope > 0)`

#### Table: `recall_affected_deliveries`
- **Primary Key:** `id INTEGER AUTO_INCREMENT`
- **Foreign Keys:**
  - `recall_id` -> `recall_cases(recall_id)` ON DELETE CASCADE
  - `delivery_id` -> `deliveries(delivery_id)` ON DELETE CASCADE
- **Constraints:**
  - `CHECK (qty_in_scope > 0)`

#### Table: `exception_records`
- **Primary Key:** `exception_id VARCHAR(20)`
- **Constraints:**
  - `CHECK (issue_type IN ('MISSING_INPUT_LOT', 'DELIVERY_OVERRUN', 'MISSED_CUSTOMER', 'INVENTORY_NOT_QUARANTINED'))`
