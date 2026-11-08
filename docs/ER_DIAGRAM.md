# Entity-Relationship Diagram (ERD): YottaFlex SCM

**Project:** YottaFlex Supply Chain Traceability and Recall Management System  
**Seed Reference:** `20261022`

---

## 1. Relational Entity Architecture

The diagram below illustrates the end-to-end data model tracing from raw materials to final customer deliveries and the overlying recall management system.

```mermaid
erDiagram
    SUPPLIERS ||--o{ MATERIAL_LOTS : "supplies"
    PRODUCTS ||--o{ BOM_ITEMS : "has_recipe"
    PRODUCTS ||--o{ PRODUCTION_ORDERS : "manufactured_via"
    PRODUCTS ||--o{ FINISHED_LOTS : "produces"
    
    PRODUCTION_ORDERS ||--o{ PRODUCTION_CONSUMPTIONS : "consumes"
    MATERIAL_LOTS ||--o{ PRODUCTION_CONSUMPTIONS : "issued_to"
    
    PRODUCTION_ORDERS ||--o{ FINISHED_LOTS : "yields"
    
    FINISHED_LOTS ||--o{ LOT_GENEALOGY : "has_provenance"
    MATERIAL_LOTS ||--o{ LOT_GENEALOGY : "contributes_to"
    
    FINISHED_LOTS ||--o{ SHIPMENTS : "dispatched_in"
    SHIPMENTS ||--o{ DELIVERIES : "fulfills"
    CUSTOMERS ||--o{ DELIVERIES : "receives"
    
    RECALL_CASES ||--o{ RECALL_ACTIONS : "executes"
    RECALL_CASES ||--o{ RECALL_AFFECTED_FINISHED_LOTS : "traps_batch"
    FINISHED_LOTS ||--o{ RECALL_AFFECTED_FINISHED_LOTS : "implicated_in"
    
    RECALL_CASES ||--o{ RECALL_AFFECTED_DELIVERIES : "traps_delivery"
    DELIVERIES ||--o{ RECALL_AFFECTED_DELIVERIES : "implicated_in"

    SUPPLIERS {
        string supplier_id PK
        string name
        string country
        string category
        string contact_email
        numeric reliability_score
    }

    MATERIAL_LOTS {
        string lot_id PK
        string supplier_id FK
        string material_type
        numeric quantity_kg
        numeric qty_remaining_kg
        date receipt_date
        date expiry_date
        string status
    }

    PRODUCTS {
        string product_id PK
        string name
        string sku UK
        string category
        string uom
        int shelf_life_days
    }

    BOM_ITEMS {
        string bom_id PK
        string product_id FK
        string material_type
        numeric quantity_per_unit
    }

    PRODUCTION_ORDERS {
        string order_id PK
        string product_id FK
        numeric planned_qty
        numeric actual_qty
        date start_date
        date end_date
        string status
    }

    FINISHED_LOTS {
        string lot_id PK
        string order_id FK
        string product_id FK
        numeric quantity_produced
        numeric qty_remaining
        date production_date
        date expiry_date
        string status
    }

    LOT_GENEALOGY {
        int genealogy_id PK
        string finished_lot_id FK
        string material_lot_id FK
        string material_lot_id_ref
        numeric qty_contributed
    }

    SHIPMENTS {
        string shipment_id PK
        string finished_lot_id FK
        string carrier
        numeric qty_shipped
        date ship_date
        date expected_delivery_date
        string status
    }

    CUSTOMERS {
        string customer_id PK
        string name
        string country
        string region
        string contact_email
        string tier
    }

    DELIVERIES {
        string delivery_id PK
        string shipment_id FK
        string customer_id FK
        numeric qty_delivered
        date delivery_date
        string status
    }

    RECALL_CASES {
        string recall_id PK
        string trigger_type
        string trigger_lot_id
        string reason
        string severity
        string initiated_by
        string status
        numeric total_qty_affected
        numeric total_qty_recovered
    }

    RECALL_ACTIONS {
        string action_id PK
        string recall_id FK
        string action_type
        string target_entity_type
        string target_entity_id
        numeric qty_actioned
        string status
    }
```

---

## 2. Cardinality & Relationship Dynamics

1. **Suppliers to Material Lots (1:N):** One qualified vendor delivers hundreds of material receipt lots over time.
2. **Products to BOM Items (1:N):** A finished product recipe is composed of 2 to 6 specific raw material requirements.
3. **Production Orders to Finished Lots (1:N):** Each production order yields one or more packaged output finished lots.
4. **Lot Genealogy (N:M):** Many raw material lots contribute to multiple finished lots through partial and multi-lot dispensing.
5. **Finished Lots to Shipments (1:N):** Pallets from a finished lot are partitioned across logistics carriers.
6. **Shipments to Deliveries (1:N):** A master carrier shipment is distributed to multiple customer regional distribution centers.
7. **Recall Cases to Interventions (1:N):** A single recall case coordinates notifications, warehouse quarantines, and physical retrievals.
