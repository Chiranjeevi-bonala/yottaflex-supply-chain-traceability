# REST API Documentation: YottaFlex SCM Platform

**Base URL:** `http://localhost:8000`  
**OpenAPI Interactive Docs:** `http://localhost:8000/api/docs`  
**ReDoc Documentation:** `http://localhost:8000/api/redoc`

---

## 1. System & Health Endpoints

### `GET /health`
- **Description:** Returns service operational health and database dialect.
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "system": "YottaFlex Traceability System",
    "version": "1.0.0",
    "database": "postgresql"
  }
  ```

### `GET /api/dashboard/overview`
- **Description:** Executive dashboard summary of master volume counts, active recall status, and key metrics.
- **Response `200 OK`:**
  ```json
  {
    "status": "healthy",
    "fixed_seed": 20261022,
    "database": "sqlite",
    "volumes": {
      "suppliers": 500,
      "material_lots": 10000,
      "production_orders": 5000,
      "finished_lots": 8000,
      "shipments": 15000,
      "customers": 1000,
      "deliveries": 20001
    },
    "recalls": {
      "active_recalls_count": 10,
      "closed_recalls_count": 0,
      "total_qty_affected_kg": 54200.0,
      "total_qty_recovered_kg": 43360.0,
      "outstanding_qty_kg": 10840.0
    },
    "anomalies": {
      "total_detected": 4,
      "status": "ALERT"
    }
  }
  ```

---

## 2. Upstream Entities

### `GET /api/suppliers`
- **Query Params:** `skip` (default 0), `limit` (default 50), `category`, `country`.
- **Response `200 OK`:** Array of `SupplierResponse`.

### `GET /api/suppliers/{supplier_id}`
- **Response `200 OK`:** Single `SupplierResponse`. Returns `404` if not found.

### `GET /api/material-lots`
- **Query Params:** `skip`, `limit`, `supplier_id`, `material_type`, `status`.
- **Response `200 OK`:** Array of `MaterialLotResponse`.

### `GET /api/material-lots/{lot_id}`
- **Response `200 OK`:** Single `MaterialLotResponse`. Returns `404` if not found.

### `GET /api/material-lots/{lot_id}/trace` (Alias: `/downstream-trace`)
- **Description:** Multi-echelon forward downstream graph traversal.
- **Response `200 OK`:**
  ```json
  {
    "trigger_lot_id": "RAWLOT-SUP-000001-2026-000001",
    "trigger_type": "RAW_LOT",
    "material_type": "Enzyme",
    "supplier_id": "SUP-000001",
    "affected_finished_lots": [...],
    "affected_shipments": [...],
    "affected_deliveries": [...],
    "affected_customers": [...],
    "summary": {
      "total_finished_lots": 3,
      "total_shipments": 6,
      "total_deliveries": 8,
      "total_customers": 7,
      "total_produced_affected_kg": 3500.0,
      "total_delivered_affected_kg": 3200.0
    }
  }
  ```

---

## 3. Products & Recipes

### `GET /api/products`
- **Query Params:** `skip`, `limit`, `category`, `is_active`.
- **Response `200 OK`:** Array of `ProductResponse`.

### `GET /api/products/{product_id}`
- **Response `200 OK`:** Single `ProductResponse`.

### `GET /api/products/{product_id}/bom`
- **Response `200 OK`:** Array of `BOMItemResponse` formulating the recipe.

---

## 4. Production & Manufacturing

### `GET /api/production-orders` (Alias: `/api/production/orders`)
- **Query Params:** `skip`, `limit`, `product_id`, `status`.
- **Response `200 OK`:** Array of `ProductionOrderResponse`.

### `GET /api/production-orders/{order_id}`
- **Response `200 OK`:** Single `ProductionOrderResponse`.

### `GET /api/production-orders/{order_id}/consumptions`
- **Response `200 OK`:** Array of material consumption transactions.

### `GET /api/finished-lots`
- **Query Params:** `skip`, `limit`, `product_id`, `status`.
- **Response `200 OK`:** Array of `FinishedLotResponse`.

### `GET /api/finished-lots/{lot_id}/genealogy` (Alias: `/upstream-trace`)
- **Description:** Backward upstream graph traversal to raw lots and suppliers.
- **Response `200 OK`:**
  ```json
  {
    "finished_lot_id": "FINLOT-2026-000001",
    "product_id": "PROD-000001",
    "quantity_produced": 1000.0,
    "status": "RELEASED",
    "ingredients": [
      {
        "material_lot_id_ref": "RAWLOT-SUP-000001-2026-000001",
        "qty_contributed": 350.0,
        "is_missing_in_db": false
      }
    ],
    "raw_material_lots": [...],
    "suppliers": [...]
  }
  ```

---

## 5. Logistics & Customers

### `GET /api/shipments`
- **Query Params:** `skip`, `limit`, `finished_lot_id`, `carrier`, `status`.
- **Response `200 OK`:** Array of `ShipmentResponse`.

### `GET /api/customers`
- **Query Params:** `skip`, `limit`, `tier`, `region`, `country`.
- **Response `200 OK`:** Array of `CustomerResponse`.

### `GET /api/deliveries`
- **Query Params:** `skip`, `limit`, `shipment_id`, `customer_id`, `status`.
- **Response `200 OK`:** Array of `DeliveryResponse`.

---

## 6. Safety Recall Management

### `GET /api/recalls`
- **Query Params:** `skip`, `limit`, `status`, `severity`.
- **Response `200 OK`:** Array of `RecallCaseResponse`.

### `POST /api/recalls`
- **Request Body:**
  ```json
  {
    "trigger_type": "RAW_LOT",
    "trigger_lot_id": "RAWLOT-SUP-000001-2026-000001",
    "reason": "Microbiological pathogen contamination in raw yeast",
    "severity": "CLASS_I",
    "initiated_by": "Quality Safety Directorate"
  }
  ```
- **Response `201 Created`:**
  ```json
  {
    "success": true,
    "recall_id": "REC-2026-000011",
    "trigger_lot_id": "RAWLOT-SUP-000001-2026-000001",
    "total_qty_affected": 3500.0,
    "affected_finished_lots_count": 3,
    "affected_deliveries_count": 8,
    "affected_customers_count": 7
  }
  ```

### `GET /api/recalls/{recall_id}/scope`
- **Response `200 OK`:** Detailed breakdown of affected lots and customer deliveries.

### `GET /api/recalls/{recall_id}/actions`
- **Response `200 OK`:** Array of `RecallActionResponse` audit records.

### `POST /api/recalls/{recall_id}/actions`
- **Request Body:**
  ```json
  {
    "action_type": "QUARANTINE",
    "target_entity_type": "FINISHED_LOT",
    "target_entity_id": "FINLOT-2026-000001",
    "qty_actioned": 1000.0,
    "notes": "Red tag applied; WMS pick lock verified"
  }
  ```
- **Response `201 Created`:** Action logged and finished lot status transitioned to `QUARANTINED`.

### `POST /api/recalls/{recall_id}/close`
- **Query Param:** `force` (default `false`).
- **Response `200 OK`:** Marks recall `CLOSED` if all precondition checks pass. Returns `400` with unresolved blockers if preconditions fail.

---

## 7. Exceptions & Operational Metrics

### `GET /api/exceptions`
- **Response `200 OK`:** Array of registered `ExceptionRecordResponse` items.

### `GET /api/exceptions/detected`
- **Description:** Executes live SQL audit algorithms detecting EC-01, EC-02, EC-03, and EC-04.
- **Response `200 OK`:** Detected anomaly instances, counts, and alert status.

### `GET /api/metrics`
- **Response `200 OK`:** All 8 operational metrics (M-01 to M-08) with values, percentages, formulas, and descriptions.

### `GET /api/metrics/recall`
- **Response `200 OK`:** Recall-specific operational metrics (M-02, M-03, M-05, M-06, M-07).

### `GET /api/metrics/exceptions`
- **Response `200 OK`:** Data integrity metrics (M-01, M-04, M-08).

---

## 8. Data Exports

### `GET /api/exports/csv?entity={entity_name}&limit={limit}`
- **Description:** Streams CSV attachment for download.

### `GET /api/exports/json?entity={entity_name}&limit={limit}`
- **Description:** Returns JSON array of entity records.
