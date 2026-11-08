# Data Dictionary: YottaFlex Supply Chain Traceability Platform

**Project:** YottaFlex Supply Chain Traceability and Recall Management System  
**Seed Reference:** `20261022`  
**Database Dialect:** PostgreSQL 15+ / SQLite 3 for integration tests

---

## 1. Upstream Echelon Tables

### 1.1 `suppliers`
Maintains verified commercial suppliers providing raw materials, ingredients, chemicals, and packaging.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `supplier_id` | `VARCHAR(20)` | No | PK | Unique identifier format `SUP-XXXXXX` |
| `name` | `VARCHAR(200)` | No | — | Commercial legal business entity name |
| `country` | `VARCHAR(100)` | No | — | Country of legal registration |
| `category` | `VARCHAR(30)` | No | — | `INGREDIENT`, `CHEMICAL`, or `PACKAGING` |
| `contact_email`| `VARCHAR(200)` | No | — | Urgent safety notifications inbox |
| `contact_phone`| `VARCHAR(50)` | Yes | NULL | Primary commercial telephone |
| `is_active` | `BOOLEAN` | No | `true` | Commercial activity status |
| `reliability_score`| `NUMERIC(3, 2)`| Yes | NULL | Historical vendor compliance score (0.00 to 1.00) |
| `created_at` | `TIMESTAMPTZ` | No | `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `now()` | Record modification timestamp |

### 1.2 `products`
Master catalog of manufactured finished goods stock-keeping units (SKUs).

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `product_id` | `VARCHAR(20)` | No | PK | Product code format `PROD-XXXXXX` |
| `name` | `VARCHAR(200)` | No | — | Commercial finished product trade name |
| `sku` | `VARCHAR(50)` | No | Unique | Global trade item number or SKU |
| `category` | `VARCHAR(100)` | No | — | Product classification (e.g. BEVERAGE, SNACK, PHARMA) |
| `uom` | `VARCHAR(10)` | No | — | Base unit of measure (e.g. UNIT, CASE, PALLET) |
| `shelf_life_days`| `INTEGER` | No | — | Statutory shelf life duration in days |
| `is_active` | `BOOLEAN` | No | `true` | Commercial active catalog flag |
| `created_at` | `TIMESTAMPTZ` | No | `now()` | Record creation timestamp |

### 1.3 `bom_items`
Bill of Materials (BOM) recipe defining standard ingredient input quantities per product unit.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `bom_id` | `VARCHAR(20)` | No | PK | Recipe item ID `BOM-XXXXXX` |
| `product_id` | `VARCHAR(20)` | No | FK | Reference to `products.product_id` |
| `material_type`| `VARCHAR(100)`| No | — | Required input material category/type |
| `quantity_per_unit`| `NUMERIC(12, 4)`| No | — | Standard recipe quantity required |
| `unit` | `VARCHAR(20)` | No | `'KG'` | Measurement unit |
| `is_active` | `BOOLEAN` | No | `true` | Active formulation flag |
| `created_at` | `TIMESTAMPTZ` | No | `now()` | Record creation timestamp |

### 1.4 `material_lots`
Individual receipt batches of raw materials received from qualified suppliers.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `lot_id` | `VARCHAR(60)` | No | PK | Unique lot ID `RAWLOT-{supplier}-2026-XXXXXX` |
| `supplier_id` | `VARCHAR(20)` | No | FK | Reference to `suppliers.supplier_id` |
| `material_type`| `VARCHAR(100)`| No | — | Type of raw material (e.g. Flour, Sugar, Solvent) |
| `quantity_kg` | `NUMERIC(14, 3)`| No | — | Total received physical quantity in KG |
| `qty_remaining_kg`| `NUMERIC(14, 3)`| No | — | Current unconsumed warehouse inventory in KG |
| `unit` | `VARCHAR(10)` | No | `'KG'` | Unit of measure |
| `receipt_date` | `DATE` | No | — | Goods receipt confirmation date |
| `expiry_date` | `DATE` | No | — | Manufacturer certificate of analysis expiry date |
| `status` | `VARCHAR(25)` | No | `'RECEIVED'`| `RECEIVED`, `IN_USE`, `EXHAUSTED`, `QUARANTINED` |
| `storage_location`| `VARCHAR(100)`| Yes | NULL | Warehouse bay or silo coordinates |
| `is_contaminated`| `BOOLEAN` | No | `false` | Physical contamination flag |
| `created_at` | `TIMESTAMPTZ` | No | `now()` | Record creation timestamp |

---

## 2. Production & Manufacturing Echelon

### 2.1 `production_orders`
Work orders authorized for manufacturing finished goods in factory facilities.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `order_id` | `VARCHAR(20)` | No | PK | Work order identifier `WO-2026-XXXXXX` |
| `product_id` | `VARCHAR(20)` | No | FK | Target finished product SKU |
| `planned_qty` | `NUMERIC(14, 3)`| No | — | Scheduled batch production volume |
| `actual_qty` | `NUMERIC(14, 3)`| Yes | NULL | Yielded production volume |
| `start_date` | `DATE` | No | — | Scheduled manufacturing run start date |
| `end_date` | `DATE` | Yes | NULL | Actual batch completion date |
| `status` | `VARCHAR(20)` | No | `'COMPLETED'`| `SCHEDULED`, `IN_PROGRESS`, `COMPLETED` |
| `location` | `VARCHAR(100)`| No | — | Manufacturing plant/line identifier |
| `created_at` | `TIMESTAMPTZ` | No | `now()` | Record creation timestamp |

### 2.2 `production_consumptions`
Material issue transactions recording raw material lots consumed in a specific work order.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `consumption_id`| `VARCHAR(20)` | No | PK | Transaction ID `CONS-XXXXXX` |
| `order_id` | `VARCHAR(20)` | No | FK | Reference to `production_orders.order_id` |
| `lot_id` | `VARCHAR(60)` | No | FK | Reference to `material_lots.lot_id` |
| `qty_consumed` | `NUMERIC(14, 3)`| No | — | Actual physical volume issued in KG |
| `consumed_at` | `TIMESTAMPTZ` | No | `now()` | Time of dispensing into mixing/reaction vessel |

### 2.3 `finished_lots`
Manufactured output batches yielding packaged commercial goods ready for distribution.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `lot_id` | `VARCHAR(30)` | No | PK | Finished batch ID `FINLOT-2026-XXXXXX` |
| `order_id` | `VARCHAR(20)` | No | FK | Reference to originating `production_orders.order_id` |
| `product_id` | `VARCHAR(20)` | No | FK | Reference to `products.product_id` |
| `quantity_produced`| `NUMERIC(14, 3)`| No | — | Total physical volume yielded in KG |
| `qty_remaining`| `NUMERIC(14, 3)`| No | — | Unshipped warehouse stock balance in KG |
| `production_date`| `DATE` | No | — | Manufacturing completion date |
| `expiry_date` | `DATE` | No | — | Packaged product shelf life expiration date |
| `status` | `VARCHAR(20)` | No | `'RELEASED'`| `IN_WAREHOUSE`, `RELEASED`, `QUARANTINED`, `RECALLED` |
| `storage_location`| `VARCHAR(100)`| Yes | NULL | Finished goods warehouse bin |
| `created_at` | `TIMESTAMPTZ` | No | `now()` | Record creation timestamp |

### 2.4 `lot_genealogy`
Multi-echelon N:M relational bridge establishing unbroken material provenance between raw material lots and finished lots.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `genealogy_id` | `INTEGER` | No | PK (Auto) | Surrogate bridge identifier |
| `finished_lot_id`| `VARCHAR(30)` | No | FK | Finished product lot |
| `material_lot_id_ref`| `VARCHAR(60)`| No | — | Literal input lot reference string |
| `material_lot_id`| `VARCHAR(60)` | Yes | FK (Null) | Foreign key to `material_lots.lot_id` (Null on EC-01) |
| `qty_contributed`| `NUMERIC(14, 3)`| No | — | Input volume incorporated into this finished batch |
| `created_at` | `TIMESTAMPTZ` | No | `now()` | Record creation timestamp |

---

## 3. Downstream Logistics Echelon

### 3.1 `shipments`
Carrier dispatches transporting finished lots from factory distribution centers.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `shipment_id` | `VARCHAR(20)` | No | PK | Bill of lading ID `SHP-2026-XXXXXX` |
| `finished_lot_id`| `VARCHAR(30)` | No | FK | Dispatched finished goods batch |
| `carrier` | `VARCHAR(100)`| No | — | Logistics carrier (e.g. DHL, FedEx, UPS) |
| `ship_date` | `DATE` | No | — | Date dispatched from warehouse bay |
| `expected_delivery_date`| `DATE` | No | — | Scheduled transit arrival date |
| `actual_delivery_date` | `DATE` | Yes | NULL | Carrier proof-of-delivery timestamp date |
| `status` | `VARCHAR(20)` | No | `'DELIVERED'`| `CREATED`, `IN_TRANSIT`, `DELIVERED` |
| `qty_shipped` | `NUMERIC(14, 3)`| No | — | Gross shipment weight in KG |
| `destination_region`| `VARCHAR(100)`| Yes | NULL | Geographic destination (e.g. NA-East, EMEA-West) |
| `tracking_number`| `VARCHAR(100)`| Yes | NULL | Carrier tracking barcode |

### 3.2 `customers`
Commercial retail, wholesale, and institutional customer accounts receiving finished products.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `customer_id` | `VARCHAR(20)` | No | PK | Account code `CUST-XXXXXX` |
| `name` | `VARCHAR(200)` | No | — | Business corporate entity name |
| `country` | `VARCHAR(100)` | No | — | Customer headquarters country |
| `region` | `VARCHAR(100)` | No | — | Operating logistics region |
| `contact_email`| `VARCHAR(200)` | No | — | Statutory safety recall notice inbox |
| `tier` | `VARCHAR(10)` | No | `'STANDARD'`| `PLATINUM`, `GOLD`, `SILVER`, `STANDARD` |
| `is_active` | `BOOLEAN` | No | `true` | Active trading account status |

### 3.3 `deliveries`
Proof-of-delivery confirmations documenting receipt by specific customer accounts.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `delivery_id` | `VARCHAR(20)` | No | PK | Delivery receipt ID `DEL-XXXXXX` |
| `shipment_id` | `VARCHAR(20)` | No | FK | Associated carrier shipment |
| `customer_id` | `VARCHAR(20)` | No | FK | Receiving customer account |
| `qty_delivered`| `NUMERIC(14, 3)`| No | — | Confirmed weight delivered in KG |
| `delivery_date`| `DATE` | No | — | Customer physical sign-off date |
| `status` | `VARCHAR(20)` | No | `'DELIVERED'`| `DELIVERED`, `REJECTED`, `RETURNED` |
| `notes` | `TEXT` | Yes | NULL | Delivery notes or anomaly annotations |

---

## 4. Recall Lifecycle & Audit Echelon

### 4.1 `recall_cases`
Statutory and quality safety recall incidents initiated upon contamination detection.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `recall_id` | `VARCHAR(20)` | No | PK | Recall case ID `REC-2026-XXXXXX` |
| `trigger_type` | `VARCHAR(15)` | No | — | `RAW_LOT` or `FINISHED_LOT` |
| `trigger_lot_id`| `VARCHAR(60)` | No | — | Lot ID initiating the recall investigation |
| `reason` | `TEXT` | No | — | Microbiological, chemical, or physical hazard rationale |
| `severity` | `VARCHAR(10)` | No | `'CLASS_II'`| FDA/Statutory severity: `CLASS_I`, `CLASS_II`, `CLASS_III` |
| `initiated_by` | `VARCHAR(100)`| No | `'System Quality Officer'` | Officer or system role initiating case |
| `initiated_at` | `TIMESTAMPTZ` | No | `now()` | Case activation timestamp |
| `closed_at` | `TIMESTAMPTZ` | Yes | NULL | Case closure timestamp (requires all preconditions) |
| `status` | `VARCHAR(15)` | No | `'OPEN'` | `OPEN`, `IN_PROGRESS`, `CLOSED` |
| `total_qty_affected`| `NUMERIC(14, 3)`| Yes | NULL | Total production volume within scope in KG |
| `total_qty_recovered`| `NUMERIC(14, 3)`| No | `0` | Cumulative volume recovered or destroyed in KG |

### 4.2 `recall_actions`
Audit log of specific interventions executed under an active recall case.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `action_id` | `VARCHAR(20)` | No | PK | Action log ID `ACT-XXXXXX` |
| `recall_id` | `VARCHAR(20)` | No | FK | Parent recall case |
| `action_type` | `VARCHAR(15)` | No | — | `NOTIFY`, `QUARANTINE`, or `RECOVER` |
| `target_entity_type`| `VARCHAR(20)`| No | — | `CUSTOMER`, `FINISHED_LOT`, `SHIPMENT`, `DELIVERY` |
| `target_entity_id`| `VARCHAR(60)`| No | — | ID of target customer or lot |
| `qty_affected` | `NUMERIC(14, 3)`| Yes | NULL | Volume affected by this specific action |
| `qty_actioned` | `NUMERIC(14, 3)`| Yes | NULL | Volume recovered or quarantined in KG |
| `actioned_at` | `TIMESTAMPTZ` | No | `now()` | Timestamp of action execution |
| `status` | `VARCHAR(15)` | No | `'COMPLETED'`| `PENDING`, `COMPLETED`, `FAILED` |
| `notes` | `TEXT` | Yes | NULL | Execution documentation or BOL reference |

### 4.3 `recall_affected_finished_lots`
Relational join table registering finished lots trapped within downstream recall scope.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `INTEGER` | No | PK (Auto) | Surrogate join identifier |
| `recall_id` | `VARCHAR(20)` | No | FK | Parent recall case |
| `finished_lot_id`| `VARCHAR(30)`| No | FK | In-scope finished lot |
| `qty_in_scope` | `NUMERIC(14, 3)`| No | — | Manufactured volume in scope in KG |

### 4.4 `recall_affected_deliveries`
Relational join table registering customer deliveries trapped within downstream recall scope.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `INTEGER` | No | PK (Auto) | Surrogate join identifier |
| `recall_id` | `VARCHAR(20)` | No | FK | Parent recall case |
| `delivery_id` | `VARCHAR(20)`| No | FK | In-scope customer delivery |
| `qty_in_scope` | `NUMERIC(14, 3)`| No | — | Delivered volume in scope in KG |

### 4.5 `exception_records`
Ground-truth anomaly benchmarks and audit records cataloging injected edge cases.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `exception_id` | `VARCHAR(20)` | No | PK | Anomaly ID `EXC-XXXXXX` |
| `issue_type` | `VARCHAR(30)` | No | — | `MISSING_INPUT_LOT`, `DELIVERY_OVERRUN`, `MISSED_CUSTOMER`, `INVENTORY_NOT_QUARANTINED` |
| `entity_type` | `VARCHAR(30)` | No | — | Entity class (e.g. `FINISHED_LOT`, `CUSTOMER`) |
| `entity_id` | `VARCHAR(60)` | No | — | Target entity identifier |
| `detection_status`| `VARCHAR(20)`| No | `'DETECTED'` | Engine detection confirmation |
| `impact_description`| `TEXT` | No | — | Operational and consumer safety risk statement |
| `expected_decision`| `TEXT` | No | — | Prescribed standard operating procedure remediation |
| `ground_truth_label`| `JSON` | Yes | NULL | Isolated ground-truth evaluation metadata |
