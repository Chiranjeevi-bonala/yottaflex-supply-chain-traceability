# Four Mandatory Edge Cases: Specification & Detection Protocols

**Project:** YottaFlex Supply Chain Traceability and Recall Management System  
**Seed Reference:** `20261022`

---

## 1. Architectural Philosophy: Ground-Truth Isolation

To guarantee scientific and engineering integrity, YottaFlex enforces strict **Ground-Truth Isolation**:
1. Synthetic anomalies are injected into baseline operational tables as realistic data corruptions (e.g., null foreign keys, inflated delivery quantities, omitted action events).
2. Ground-truth benchmark records are stored separately in `exports/ground_truth/ground_truth.json` and `ground_truth.csv`.
3. The automated audit algorithms in `ExceptionDetector` operate **strictly on live operational tables** using standard relational logic.
4. Ground-truth labels are never queried by detection routines, ordinary API endpoints, or operational dashboard displays.

---

## 2. Specification of Mandatory Edge Cases

### 2.1 EC-01: Missing Input Lot (`MISSING_INPUT_LOT`)

#### Description
A manufactured finished lot references an input raw material lot string in its batch consumption log, but no corresponding receipt record exists in the supplier lot master table.

#### Root Cause Simulation
ERP replication lag, barcode scanning typo, or unauthorized substitution of unapproved vendor material.

#### Injection Mechanism
- Appends a record to `lot_genealogy`:
  - `finished_lot_id = "FINLOT-2026-000011"`
  - `material_lot_id_ref = "RAWLOT-SUP-999999-2026-999999"`
  - `material_lot_id = NULL` (violates relational reference)

#### Operational Detection Query
```sql
SELECT g.finished_lot_id, g.material_lot_id_ref, g.qty_contributed
FROM lot_genealogy g
WHERE g.material_lot_id IS NULL;
```

#### Operational Impact
Loss of upstream provenance; potential unverified allergen, pathogen, or unapproved chemical additive; regulatory non-compliance under FDA FSMA Section 204.

#### Remediation Protocol
Execute immediate ERP hold on finished lot; quarantine batch in warehouse; review physical paper batch tickets and COA to identify true vendor lot.

---

### 2.2 EC-02: Delivery Overrun (`DELIVERY_OVERRUN`)

#### Description
The cumulative sum of quantities delivered to customers for a given finished lot exceeds the total physical volume manufactured in that production run.

#### Root Cause Simulation
Duplicate proof-of-delivery scanning, phantom shipment creation, or failure to record a secondary rework production order.

#### Injection Mechanism
- Injects a duplicate delivery record into `deliveries`:
  - `finished_lot_id = "FINLOT-2026-000026"` (produced: 1,000 kg)
  - Existing delivery: 1,000 kg
  - Injected overrun delivery: 500 kg
  - Total delivered: 1,500 kg (overrun = 500 kg)

#### Operational Detection Query
```sql
SELECT 
    fl.lot_id,
    fl.quantity_produced,
    SUM(d.qty_delivered) AS total_delivered,
    (SUM(d.qty_delivered) - fl.quantity_produced) AS overrun_quantity
FROM finished_lots fl
JOIN shipments s ON s.finished_lot_id = fl.lot_id
JOIN deliveries d ON d.shipment_id = s.shipment_id
GROUP BY fl.lot_id, fl.quantity_produced
HAVING SUM(d.qty_delivered) > fl.quantity_produced;
```

#### Operational Impact
Inventory phantom stock; potential unrecorded parallel production; freight carrier billing overcharges; financial revenue misstatement.

#### Remediation Protocol
Freeze logistics carrier settlement; conduct physical count of remaining warehouse pallets; audit carrier bills of lading against customer delivery receipts.

---

### 2.3 EC-03: Missed Downstream Customer (`MISSED_CUSTOMER`)

#### Description
A commercial customer received a confirmed delivery of product belonging to a recalled batch, but was omitted from the emergency safety notification registry.

#### Root Cause Simulation
Communication failure, outdated customer contact record, or manual exclusion from notification blast.

#### Injection Mechanism
- Identifies an active recall case `REC-2026-000001` with customer deliveries in scope.
- Deletes or suppresses the `NOTIFY` action in `recall_actions` for customer `CUST-000001`.

#### Operational Detection Query
```sql
WITH scope_customers AS (
    SELECT DISTINCT d.customer_id, rad.recall_id
    FROM recall_affected_deliveries rad
    JOIN deliveries d ON d.delivery_id = rad.delivery_id
),
notified_customers AS (
    SELECT DISTINCT ra.target_entity_id AS customer_id, ra.recall_id
    FROM recall_actions ra
    WHERE ra.action_type = 'NOTIFY' AND ra.target_entity_type = 'CUSTOMER'
)
SELECT sc.recall_id, sc.customer_id
FROM scope_customers sc
LEFT JOIN notified_customers nc 
    ON sc.customer_id = nc.customer_id AND sc.recall_id = nc.recall_id
WHERE nc.customer_id IS NULL;
```

#### Operational Impact
End-consumer exposure to adulterated or hazardous product; severe regulatory penalties; product liability litigation.

#### Remediation Protocol
Dispatch emergency priority certified telegram; trigger automated CRM escalation; deploy regional territory sales representative for physical verification.

---

### 2.4 EC-04: Inventory Not Quarantined (`INVENTORY_NOT_QUARANTINED`)

#### Description
A manufactured finished lot caught within the scope of an active safety recall remains in `status = 'IN_WAREHOUSE'` with available unsold inventory.

#### Root Cause Simulation
WMS lock failure, warehouse operator oversight, or delay in applying physical quarantine signage.

#### Injection Mechanism
- Sets in-scope lot `FINLOT-2026-000051`:
  - `status = 'IN_WAREHOUSE'`
  - `qty_remaining = 350.0 kg`
- Removes any `QUARANTINE` action in `recall_actions`.

#### Operational Detection Query
```sql
SELECT 
    rc.recall_id,
    fl.lot_id,
    fl.qty_remaining,
    fl.status
FROM recall_cases rc
JOIN recall_affected_finished_lots rafl ON rafl.recall_id = rc.recall_id
JOIN finished_lots fl ON fl.lot_id = rafl.finished_lot_id
WHERE rc.status IN ('OPEN', 'IN_PROGRESS')
  AND fl.status = 'IN_WAREHOUSE'
  AND fl.qty_remaining > 0;
```

#### Operational Impact
Severe risk of warehouse pickers staging and shipping contaminated pallets to commercial customers during an ongoing recall.

#### Remediation Protocol
Execute immediate automated ERP pick-lock; apply red physical tag on warehouse bins; move pallets to restricted-access locked quarantine cage.
