# Source Code Manifest: YottaFlex SCM Repository

**Project:** YottaFlex Supply Chain Traceability and Recall Management System  
**Seed Reference:** `20261022`

---

## 1. Repository Inventory by Subsystem

### 1.1 Backend Core & API Layer (`backend/app`)
| File Path | Subsystem | Responsibility |
|---|---|---|
| `backend/app/main.py` | API Entrypoint | FastAPI application instantiation, CORS, routers, lifespan events, `/health`. |
| `backend/app/config.py` | Settings | Pydantic V2 `Settings` for database URL, random seed, debug mode. |
| `backend/app/database.py` | Database Session | SQLAlchemy engine, session maker, `get_db` dependency, table creation. |
| `backend/app/schemas/entities.py` | Data Validation | Pydantic response and request models with `ConfigDict(from_attributes=True)`. |

### 1.2 SQLAlchemy Relational ORM Models (`backend/app/models`)
| File Path | Entity Mapped | Responsibility |
|---|---|---|
| `backend/app/models/base.py` | Declarative Base | Common `Base` model for SQLAlchemy. |
| `backend/app/models/supplier.py` | `suppliers` | Supplier master with country, category, reliability score. |
| `backend/app/models/product.py` | `products` | Product catalog with SKU, shelf life, and active flag. |
| `backend/app/models/bom.py` | `bom_items` | Recipe specifications linking products to material types. |
| `backend/app/models/material_lot.py` | `material_lots` | Raw material receipt lots with remaining balance. |
| `backend/app/models/production_order.py` | `production_orders` | Factory work orders with planned and actual volumes. |
| `backend/app/models/production_consumption.py` | `production_consumptions` | Material consumption transactions per work order. |
| `backend/app/models/finished_lot.py` | `finished_lots` | Manufactured finished product batches. |
| `backend/app/models/lot_genealogy.py` | `lot_genealogy` | N:M provenance bridge linking finished lots to raw lots. |
| `backend/app/models/shipment.py` | `shipments` | Logistics carrier dispatches. |
| `backend/app/models/customer.py` | `customers` | Commercial accounts receiving product. |
| `backend/app/models/delivery.py` | `deliveries` | Customer delivery receipts. |
| `backend/app/models/recall_case.py` | `recall_cases` | Statutory safety recall cases. |
| `backend/app/models/recall_action.py` | `recall_actions` | Action log (`NOTIFY`, `QUARANTINE`, `RECOVER`). |
| `backend/app/models/recall_affected_finished_lot.py` | `recall_affected_finished_lots` | Finished lots caught in recall scope. |
| `backend/app/models/recall_affected_delivery.py` | `recall_affected_deliveries` | Customer deliveries caught in recall scope. |
| `backend/app/models/exception_record.py` | `exception_records` | Ground-truth anomaly definitions. |

### 1.3 Core Business Engines (`backend/app/engine`)
| File Path | Engine Component | Responsibility |
|---|---|---|
| `backend/app/engine/genealogy.py` | Genealogy Traversal | Multi-echelon forward and backward graph traversal algorithms. |
| `backend/app/engine/recall_engine.py` | Recall Orchestrator | Scope calculation, action logging, and pre-closure validation. |
| `backend/app/engine/exception_detector.py` | Anomaly Auditing | Live SQL detectors for EC-01, EC-02, EC-03, and EC-04. |
| `backend/app/engine/metrics.py` | Operational Metrics | Mathematical computation of metrics M-01 through M-08. |

### 1.4 REST API Routers (`backend/app/routers`)
| File Path | Route Prefix | Responsibility |
|---|---|---|
| `backend/app/routers/dashboard.py` | `/api/dashboard` | Executive overview KPI aggregates. |
| `backend/app/routers/suppliers.py` | `/api/suppliers` | Supplier list, search, and detail. |
| `backend/app/routers/material_lots.py`| `/api/material-lots` | Lot list, detail, and `/trace` endpoint. |
| `backend/app/routers/products.py` | `/api/products` | Catalog list, detail, and `/bom` recipe. |
| `backend/app/routers/production.py` | `/api/production-orders` | Work orders and consumption logs. |
| `backend/app/routers/finished_lots.py`| `/api/finished-lots` | Finished batches and `/genealogy` endpoint. |
| `backend/app/routers/shipments.py` | `/api/shipments` | Carrier dispatch manifests. |
| `backend/app/routers/customers.py` | `/api/customers` | Account details and order history. |
| `backend/app/routers/deliveries.py` | `/api/deliveries` | Customer proof of delivery records. |
| `backend/app/routers/recalls.py` | `/api/recalls` | Recall lifecycle, scope, actions, and closure. |
| `backend/app/routers/exceptions.py` | `/api/exceptions` | Anomaly records and live audit reports. |
| `backend/app/routers/metrics.py` | `/api/metrics` | Live operational performance evaluations. |
| `backend/app/routers/exports.py` | `/api/exports` | CSV and JSON file streaming endpoints. |

### 1.5 Synthetic Data Pipeline (`backend/data`)
| File Path | Component | Responsibility |
|---|---|---|
| `backend/data/generators/config.py` | Scale Configurations | Fixed seed (`20261022`), starter, medium, full scales. |
| `backend/data/generators/id_gen.py` | ID Nomenclature | Standardized zero-padded unique IDs. |
| `backend/data/generators/pipeline.py`| Master Pipeline | 12-stage sequential generation and export orchestration. |
| `backend/data/generators/edge_case_injector.py` | Anomaly Injector | Separately injects EC-01..04 with isolated ground truth. |
| `backend/data/exports/csv_exporter.py` | CSV Export | Exports all 16 tables to CSV format. |
| `backend/data/exports/json_exporter.py`| JSON Export | Exports all 16 tables to formatted JSON. |
| `backend/data/exports/sql_exporter.py` | SQL Export | Generates PostgreSQL/SQLite `seed.sql`. |
| `backend/data/exports/ground_truth_exporter.py` | GT Export | Exports isolated ground truth datasets. |

### 1.6 Frontend Enterprise Console (`frontend`)
| File Path | Component | Responsibility |
|---|---|---|
| `frontend/package.json` | Project Definition | React 18, Vite, Tailwind CSS, TypeScript. |
| `frontend/vite.config.ts` | Vite Config | Build bundler configuration. |
| `frontend/tsconfig.json` | TS Config | Strict TypeScript compiler options. |
| `frontend/tailwind.config.js` | Styling Config | Tailwind theme and dark-mode styling. |
| `frontend/src/App.tsx` | Main Dashboard | 16-section interactive enterprise operations console. |
| `frontend/src/main.tsx` | React Root | DOM hydration entrypoint. |
| `frontend/src/index.css` | Global CSS | Tailwind directives and custom scrollbars. |

### 1.7 Documentation Suite (`docs/` & Root)
- `README.md`
- `docs/PROJECT_AUDIT.md`
- `docs/PROJECT_STATUS.md`
- `docs/REQUIREMENT_TRACEABILITY_MATRIX.md`
- `docs/DATA_DICTIONARY.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/ER_DIAGRAM.md`
- `docs/GENEALOGY_DESIGN.md`
- `docs/RECALL_WORKFLOW.md`
- `docs/EDGE_CASES.md`
- `docs/METRICS_DEFINITIONS.md`
- `docs/GENERATOR_GUIDE.md`
- `docs/API_DOCUMENTATION.md`
- `docs/VALIDATION_SUMMARY.md`
- `docs/SOURCE_MANIFEST.md`
