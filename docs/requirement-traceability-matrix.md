# Requirement Traceability Matrix (RTM)

| Req ID | Official Requirement | Implementation Module | Expected Output | Validation Method | Test Case | Status |
|---|---|---|---|---|---|---|
| **FR-01.1** | Register suppliers | `app/models/supplier.py` | 500 supplier rows | PK uniqueness & check constraints | `test_id_generator_formats` | ✅ Complete |
| **FR-01.2** | Register raw material lots linked to suppliers | `app/models/material_lot.py` | 10,000 lot rows | Foreign Key integrity | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-01.3** | Register products and BOMs | `app/models/product.py`, `app/models/bom.py` | Product + BOM items | BOM to Product FK & Unique constraint | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-01.4** | Create production orders | `app/models/production_order.py` | 5,000 order rows | Work order FK & status lifecycle | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-02.1** | Consume raw lots into production per BOM | `data/generators/production_gen.py` | Consumption bridge rows | Consumed qty <= lot available qty | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-02.2** | Validate BOM consumption requirements | `app/engine/genealogy.py` | Ingredient verification | Trace upstream BOM alignment | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-02.3** | Generate finished lots | `app/models/finished_lot.py` | 8,000 finished lots | Work Order FK & positive quantity | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-02.4** | Finished lot ↔ Raw lot genealogy (N:M) | `app/models/lot_genealogy.py` | LotGenealogy bridge rows | FinishedLot links to >= 1 RawLot | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-03.1** | Associate finished lots with shipments | `app/models/shipment.py` | 1 FINLOT -> 1+ Shipments | FK integrity, shipped <= produced | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-03.2** | Track shipments to customer deliveries | `app/models/delivery.py` | 20,000 deliveries | Delivery FK to shipment & customer | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-03.3** | Record delivered quantity | `app/models/delivery.py` | Positive delivered qty | CheckConstraint(qty_delivered > 0) | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-03.4** | Validate delivered <= shipment quantity | `data/generators/distribution_gen.py` | Reconciled deliveries | Sum(delivered) <= shipped | `test_metrics_calculation` | ✅ Complete |
| **FR-04.1** | Create recall triggers | `app/models/recall_case.py` | RecallCase row (OPEN) | Trigger lot FK validation | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-04.2** | Traverse downstream genealogy | `app/engine/genealogy.py` | Graph traversal result | Matches physical lot linkages | `test_genealogy_downstream_and_upstream` | ✅ Complete |
| **FR-04.3** | Identify affected finished lots | `app/engine/genealogy.py` | Set of affected FINLOT IDs | Graph node reachable check | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-04.4** | Identify affected shipments | `app/engine/genealogy.py` | List of SHP IDs | Shipment FK check | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-04.5** | Identify affected customers | `app/engine/genealogy.py` | Set of customer IDs | Customer reachability | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-04.6** | Calculate affected quantities | `app/engine/recall_engine.py` | Total kg affected | Reconciles with produced/delivered | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-04.7** | Record notification actions | `app/models/recall_action.py` | RecallAction(NOTIFY) | Action log insertion | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-04.8** | Record inventory quarantine | `app/models/recall_action.py` | RecallAction(QUARANTINE) | Lot status updated to QUARANTINED | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-04.9** | Track recovered quantities | `app/models/recall_action.py` | RecallAction(RECOVER) | Cumulative recovery tracking | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-04.10**| Calculate remaining unrecovered | `app/engine/recall_engine.py` | Remaining qty balance | affected - recovered calculation | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-04.11**| Recall completion status | `app/engine/recall_engine.py` | Status CLOSED | Condition: remaining = 0 or verified | `test_recall_engine_lifecycle` | ✅ Complete |
| **FR-05.1** | Detect missing input lot (EC-01) | `app/engine/exception_detector.py` | `MISSING_INPUT_LOT` record | LotGenealogy where material_lot_id is null | `test_exception_detector_all_four_scenarios` | ✅ Complete |
| **FR-05.2** | Detect delivery overrun (EC-02) | `app/engine/exception_detector.py` | `DELIVERY_OVERRUN` record | Delivered sum > produced qty | `test_exception_detector_all_four_scenarios` | ✅ Complete |
| **FR-05.3** | Detect missed recall customer (EC-03) | `app/engine/exception_detector.py` | `MISSED_CUSTOMER` record | Scope customers without NOTIFY action | `test_exception_detector_all_four_scenarios` | ✅ Complete |
| **FR-05.4** | Detect unquarantined stock (EC-04) | `app/engine/exception_detector.py` | `INVENTORY_NOT_QUARANTINED` | Recalled lot status == IN_WAREHOUSE | `test_exception_detector_all_four_scenarios` | ✅ Complete |
| **FR-06.1–8**| 8 Operational metrics | `app/engine/metrics.py` | Live metric dictionary | Formula mathematical verification | `test_metrics_calculation` | ✅ Complete |
| **TR-01.1–5**| Exact volume targets | `data/generators/config.py` | 500/10k/5k/8k/20k | Count assertion | `test_fixed_seed_deterministic_reproducibility` | ✅ Complete |
| **TR-01.6** | Fixed seed: 20261022 | `data/generators/config.py` | Deterministic outputs | Dual-run checksum match | `test_fixed_seed_deterministic_reproducibility` | ✅ Complete |
| **TR-01.7–11**| ID nomenclature conventions | `data/generators/id_gen.py` | Exact prefixes & zero-padding | Regex validation | `test_id_generator_formats` | ✅ Complete |
| **TR-07.1–4**| Data exports (CSV/JSON/SQL/GT) | `data/exports/*.py` | Formatted export files | File existence and row verification | Verified in pipeline run | ✅ Complete |

