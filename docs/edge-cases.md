# Required Edge Cases & Negative Scenarios Analysis

Treatment of the four mandatory negative scenarios in the YottaFlex Traceability System.

---

## 1. Scenario Summary Matrix

| ID | Issue Type | Injection Strategy | Detection Algorithm | Operational Impact | Recommended Protocol |
|---|---|---|---|---|---|
| **EC-01** | `MISSING_INPUT_LOT` | Injects `LotGenealogy` row with `material_lot_id=None` pointing to a fabricated ID. | `WHERE lot_genealogy.material_lot_id IS NULL` | Loss of upstream traceability; potential unverified allergen or contaminant. | Quarantine finished lot immediately; audit production ERP batch tickets. |
| **EC-02** | `DELIVERY_OVERRUN` | Injects/inflates `Delivery.qty_delivered` so sum of deliveries > produced quantity. | Group deliveries by `finished_lot_id`, compare sum against `quantity_produced`. | Inventory phantom stock; billing errors; fraudulent unrecorded production. | Halt invoice clearing; initiate warehouse physical stock vs ERP count audit. |
| **EC-03** | `MISSED_CUSTOMER` | Omit `NOTIFY` `RecallAction` for one affected customer in active recall. | Set difference: `Scope Customers \ Notified Customers`. | Consumer health liability; regulatory non-compliance penalty. | Dispatch emergency priority telegram; alert compliance team. |
| **EC-04** | `INVENTORY_NOT_QUARANTINED` | Retain `status="IN_WAREHOUSE"` with positive `qty_remaining` under active recall. | `WHERE FinishedLot.status == 'IN_WAREHOUSE' AND lot_id IN (Recall Scope)`. | Contaminated inventory risks accidental shipment to customers during recall. | Lock warehouse storage bay; place physical quarantine tape on bins. |

---

## 2. Ground-Truth Data Isolation Principle

> [!IMPORTANT]
> In accordance with strict software engineering standards, **ground-truth labels are never leaked into application input features or detection logic**.

- Ground-truth anomaly records are exported separately to `exports/ground_truth/ground_truth.json` and `exports/ground_truth/ground_truth.csv`.
- The `ExceptionDetector` queries raw transactional tables (`lot_genealogy`, `deliveries`, `finished_lots`, `recall_actions`) to detect anomalies objectively.

