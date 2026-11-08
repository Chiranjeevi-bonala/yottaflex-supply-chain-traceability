# Requirement Traceability Matrix (RTM)

**Project:** YottaFlex Supply Chain Traceability and Recall Management System  
**Seed Reference:** `20261022`  
**Last Verified:** November 8, 2026

| Req ID | Requirement Description | Architecture Module | Expected Deliverable | Verification Method | Status |
|---|---|---|---|---|---|
| **FR-01.1** | Supplier Management | `app/models/supplier.py` | 500 supplier entities | Unit test & API endpoint | **COMPLETED** |
| **FR-01.2** | Raw Material Lot Tracking | `app/models/material_lot.py` | 10,000 raw material lots | FK integrity & API test | **COMPLETED** |
| **FR-01.3** | Products & BOM Items | `app/models/product.py`, `bom.py` | 50 products with multi-item BOMs | Product & BOM routers | **COMPLETED** |
| **FR-01.4** | Production Order Tracking | `app/models/production_order.py` | 5,000 production work orders | Order status & date constraints | **COMPLETED** |
| **FR-02.1** | Raw Material Consumption | `app/models/production_consumption.py` | Actual lot-level consumption | Quantity balance check | **COMPLETED** |
| **FR-02.2** | BOM Recipe Validation | `app/engine/genealogy.py` | Ingredient verification | Upstream traversal validation | **COMPLETED** |
| **FR-02.3** | Finished Product Lot Creation | `app/models/finished_lot.py` | 8,000 finished product lots | Work order link & positive qty | **COMPLETED** |
| **FR-02.4** | Finished Lot Genealogy (N:M) | `app/models/lot_genealogy.py` | N:M raw lot to finished lot bridge | Multi-material lineage test | **COMPLETED** |
| **FR-03.1** | Shipment Association | `app/models/shipment.py` | Finished lots linked to carriers/shipments | Carrier tracking & ship date check | **COMPLETED** |
| **FR-03.2** | Customer Delivery Tracking | `app/models/delivery.py` | 20,000 customer delivery records | Delivery to customer FK validation | **COMPLETED** |
| **FR-03.3** | Delivered Quantity Recording | `app/models/delivery.py` | Positive delivered volume | Positive decimal constraint | **COMPLETED** |
| **FR-03.4** | Delivery Overrun Validation | `app/engine/exception_detector.py` | Detect delivered > produced | EC-02 detector query | **COMPLETED** |
| **FR-04.1** | Recall Case Initiation | `app/models/recall_case.py` | Formal recall case creation | Unique REC ID & trigger lot link | **COMPLETED** |
| **FR-04.2** | Downstream Scope Calculation | `app/engine/genealogy.py` | Graph traversal of affected echelon | Echelon node reachability | **COMPLETED** |
| **FR-04.3** | Identify Affected Finished Lots | `app/engine/recall_engine.py` | Affected finished lots in scope table | Graph reachability verification | **COMPLETED** |
| **FR-04.4** | Identify Affected Shipments | `app/engine/recall_engine.py` | Shipments transporting affected lots | Shipment FK query | **COMPLETED** |
| **FR-04.5** | Identify Affected Customers | `app/engine/recall_engine.py` | Recipient customers identified | Delivery destination query | **COMPLETED** |
| **FR-04.6** | Affected Quantity Aggregation | `app/engine/recall_engine.py` | Total kg affected calculated | Reconciles with produced & delivered | **COMPLETED** |
| **FR-04.7** | Customer Notification Logging | `app/models/recall_action.py` | `NOTIFY` action event logging | Action table entry with timestamp | **COMPLETED** |
| **FR-04.8** | Inventory Quarantine Recording | `app/models/recall_action.py` | `QUARANTINE` action & status update | FinishedLot.status updated | **COMPLETED** |
| **FR-04.9** | Recovered Quantity Tracking | `app/models/recall_action.py` | `RECOVER` action & sum tracking | Recall.total_qty_recovered update | **COMPLETED** |
| **FR-04.10**| Outstanding Quantity Balance | `app/engine/recall_engine.py` | Remaining unrecovered balance | `affected - recovered` balance | **COMPLETED** |
| **FR-04.11**| Pre-closure Validation | `app/engine/recall_engine.py` | Block premature recall closure | Pre-closure condition checks | **COMPLETED** |
| **FR-05.1** | Missing Input Lot Detection (EC-01) | `app/engine/exception_detector.py` | Flag `MISSING_INPUT_LOT` | Query `material_lot_id IS NULL` | **COMPLETED** |
| **FR-05.2** | Delivery Overrun Detection (EC-02) | `app/engine/exception_detector.py` | Flag `DELIVERY_OVERRUN` | Query `sum(delivered) > produced` | **COMPLETED** |
| **FR-05.3** | Missed Customer Detection (EC-03) | `app/engine/exception_detector.py` | Flag `MISSED_CUSTOMER` | Query affected without `NOTIFY` | **COMPLETED** |
| **FR-05.4** | Unquarantined Stock Detection (EC-04)| `app/engine/exception_detector.py` | Flag `INVENTORY_NOT_QUARANTINED` | Recalled lot in `IN_WAREHOUSE` | **COMPLETED** |
| **FR-06.1** | M-01 Genealogy Completeness | `app/engine/metrics.py` | Live ratio calculation | Mathematical formula test | **COMPLETED** |
| **FR-06.2** | M-02 Recall Scope Accuracy | `app/engine/metrics.py` | Algorithmic scope accuracy | Ratio of traversal to scope | **COMPLETED** |
| **FR-06.3** | M-03 Notification Coverage | `app/engine/metrics.py` | Live ratio calculation | Notified / Total Affected Customers | **COMPLETED** |
| **FR-06.4** | M-04 Quantity Reconciliation Rate | `app/engine/metrics.py` | Live ratio calculation | Non-overrun / Distributed Batches | **COMPLETED** |
| **FR-06.5** | M-05 Quarantine Compliance | `app/engine/metrics.py` | Live ratio calculation | Quarantined / In-scope Batches | **COMPLETED** |
| **FR-06.6** | M-06 Recovery Rate | `app/engine/metrics.py` | Live ratio calculation | Recovered / Affected Volume | **COMPLETED** |
| **FR-06.7** | M-07 Outstanding Recall Quantity | `app/engine/metrics.py` | Outstanding volume in KG | Affected - Recovered Volume | **COMPLETED** |
| **FR-06.8** | M-08 Exception Detection Rate | `app/engine/metrics.py` | Live ratio calculation | Detected / Ground-Truth Anomalies | **COMPLETED** |
| **TR-01.1** | 500 Suppliers Target | `data/generators/config.py` | Exact volume in full scale | Count assertion | **COMPLETED** |
| **TR-01.2** | 10,000 Material Lots Target | `data/generators/config.py` | Exact volume in full scale | Count assertion | **COMPLETED** |
| **TR-01.3** | 5,000 Production Orders Target | `data/generators/config.py` | Exact volume in full scale | Count assertion | **COMPLETED** |
| **TR-01.4** | 8,000 Finished Lots Target | `data/generators/config.py` | Exact volume in full scale | Count assertion | **COMPLETED** |
| **TR-01.5** | 20,000 Deliveries Target | `data/generators/config.py` | Exact volume in full scale | Count assertion | **COMPLETED** |
| **TR-01.6** | Fixed Random Seed (`20261022`) | `data/generators/config.py` | Exact reproducibility | Dual-run checksum verification | **COMPLETED** |
| **TR-01.7** | ID Nomenclature Standards | `data/generators/id_gen.py` | Standardized zero-padded IDs | Regex format tests | **COMPLETED** |
| **TR-02.1** | REST API Endpoints Suite | `app/routers/*.py` | Full endpoint suite | FastAPI routing & schema tests | **COMPLETED** |
| **TR-03.1** | 16-Section Enterprise Dashboard | `frontend/src/*` | Full React + Vite dashboard | UI build and component tests | **COMPLETED** |
| **TR-04.1** | Multi-Format Exports | `data/exports/*.py` | CSV, JSON, SQL seed, GT | Output file verification | **COMPLETED** |
