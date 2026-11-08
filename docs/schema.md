# Database Schema Guide & Relational Constraints

## 1. Relational Architecture Overview
The database models a multi-echelon industrial supply chain across 16 tables:
1. **Master Entities**: `suppliers`, `products`, `bom_items`, `customers`
2. **Transaction Entities**: `material_lots`, `production_orders`, `finished_lots`, `shipments`, `deliveries`
3. **Traceability & Bridge Tables**: `production_consumptions`, `lot_genealogy`, `recall_affected_finished_lots`, `recall_affected_deliveries`
4. **Lifecycle & Audit Entities**: `recall_cases`, `recall_actions`, `exception_records`

---

## 2. Table Specifications & Cardinalities

### 1. `suppliers`
- **PK**: `supplier_id` VARCHAR(20) (`SUP-000001`)
- **Cardinality**: 1 Supplier : N MaterialLots
- **Constraints**: `category IN ('CHEMICAL','PACKAGING','RAW_FOOD','INGREDIENT','ADDITIVE')`, `reliability_score BETWEEN 0.0 AND 1.0`

### 2. `material_lots`
- **PK**: `lot_id` VARCHAR(60) (`RAWLOT-{supplier-id}-2026-000001`)
- **FK**: `supplier_id` -> `suppliers.supplier_id` (RESTRICT)
- **Constraints**: `quantity_kg > 0`, `qty_remaining_kg >= 0`, `qty_remaining_kg <= quantity_kg`, `expiry_date > receipt_date`
- **Lifecycle**: `RECEIVED` -> `IN_STOCK` -> `PARTIALLY_CONSUMED` -> `CONSUMED` -> `QUARANTINED` -> `DISPOSED`

### 3. `products`
- **PK**: `product_id` VARCHAR(20) (`PROD-000001`)
- **Constraints**: `sku` UNIQUE, `shelf_life_days > 0`, `uom IN ('KG','UNIT','LITER','G','MT','L')`

### 4. `bom_items`
- **PK**: `bom_id` VARCHAR(20) (`BOM-000001`)
- **FK**: `product_id` -> `products.product_id` (RESTRICT)
- **Constraints**: `quantity_per_unit > 0`, `UNIQUE(product_id, material_type)`

### 5. `production_orders`
- **PK**: `order_id` VARCHAR(20) (`WO-2026-000001`)
- **FK**: `product_id` -> `products.product_id` (RESTRICT)
- **Constraints**: `planned_qty > 0`, `end_date >= start_date`
- **Lifecycle**: `PLANNED` -> `IN_PROGRESS` -> `COMPLETED` -> `CANCELLED`

### 6. `production_consumptions`
- **PK**: `consumption_id` INTEGER (auto-increment)
- **FK**: `order_id` -> `production_orders.order_id` (CASCADE), `lot_id` -> `material_lots.lot_id` (RESTRICT)
- **Constraints**: `qty_consumed > 0`, `UNIQUE(order_id, lot_id)`

### 7. `finished_lots`
- **PK**: `lot_id` VARCHAR(30) (`FINLOT-2026-000001`)
- **FK**: `order_id` -> `production_orders.order_id` (RESTRICT), `product_id` -> `products.product_id` (RESTRICT)
- **Constraints**: `quantity_produced > 0`, `qty_remaining <= quantity_produced`, `expiry_date > production_date`
- **Lifecycle**: `PRODUCED` -> `IN_WAREHOUSE` -> `PARTIALLY_SHIPPED` -> `SHIPPED` -> `QUARANTINED` -> `RECALLED` -> `DISPOSED`

### 8. `lot_genealogy`
- **PK**: `genealogy_id` INTEGER (auto-increment)
- **FK**: `finished_lot_id` -> `finished_lots.lot_id` (CASCADE)
- **FK (Nullable for EC-01)**: `material_lot_id` -> `material_lots.lot_id` (SET NULL)
- **Raw Reference**: `material_lot_id_ref` VARCHAR(60) (Always set)
- **Constraints**: `qty_contributed > 0`, `UNIQUE(finished_lot_id, material_lot_id_ref)`

### 9. `shipments`
- **PK**: `shipment_id` VARCHAR(20) (`SHP-2026-000001`)
- **FK**: `finished_lot_id` -> `finished_lots.lot_id` (RESTRICT)
- **Constraints**: `qty_shipped > 0`, `expected_delivery_date >= ship_date`
- **Lifecycle**: `CREATED` -> `IN_TRANSIT` -> `DELIVERED` -> `RECALLED` -> `QUARANTINED`

### 10. `customers`
- **PK**: `customer_id` VARCHAR(20) (`CUST-000001`)
- **Constraints**: `tier IN ('GOLD','SILVER','BRONZE','STANDARD')`

### 11. `deliveries`
- **PK**: `delivery_id` VARCHAR(20) (`DEL-000001`)
- **FK**: `shipment_id` -> `shipments.shipment_id` (RESTRICT), `customer_id` -> `customers.customer_id` (RESTRICT)
- **Constraints**: `qty_delivered > 0`, `status IN ('DELIVERED','RETURNED','QUARANTINED')`

### 12. `recall_cases`
- **PK**: `recall_id` VARCHAR(20) (`REC-2026-000001`)
- **Constraints**: `trigger_type IN ('RAW_LOT','FINISHED_LOT')`, `severity IN ('CLASS_I','CLASS_II','CLASS_III')`, `status IN ('OPEN','IN_PROGRESS','CLOSED')`

### 13. `recall_actions`
- **PK**: `action_id` VARCHAR(20) (`ACT-000001`)
- **FK**: `recall_id` -> `recall_cases.recall_id` (CASCADE)
- **Constraints**: `action_type IN ('NOTIFY','QUARANTINE','RECOVER')`, `status IN ('PENDING','COMPLETED','FAILED')`

### 14. `recall_affected_finished_lots`
- **PK**: `id` INTEGER (auto-increment)
- **FK**: `recall_id` -> `recall_cases.recall_id` (CASCADE), `finished_lot_id` -> `finished_lots.lot_id` (CASCADE)

### 15. `recall_affected_deliveries`
- **PK**: `id` INTEGER (auto-increment)
- **FK**: `recall_id` -> `recall_cases.recall_id` (CASCADE), `delivery_id` -> `deliveries.delivery_id` (CASCADE)

### 16. `exception_records`
- **PK**: `exception_id` VARCHAR(20) (`EXC-000001`)
- **Constraints**: `issue_type IN ('MISSING_INPUT_LOT','DELIVERY_OVERRUN','MISSED_CUSTOMER','INVENTORY_NOT_QUARANTINED')`, `detection_status IN ('DETECTED','UNDETECTED')`
- **Audit Field**: `ground_truth_label` JSON (internal only)

