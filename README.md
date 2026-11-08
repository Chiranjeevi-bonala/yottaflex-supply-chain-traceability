# YottaFlex: Supply Chain Traceability & Recall Management System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![Reproducibility](https://img.shields.io/badge/Seed-20261022-green.svg)](docs/GENERATOR_GUIDE.md)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](docs/VALIDATION_SUMMARY.md)

YottaFlex is an enterprise-grade multi-echelon supply chain traceability and safety recall management system. It provides unbroken material tracking across the entire manufacturing and distribution lifecycle:

$$\text{Supplier} \longrightarrow \text{Raw Material Lots} \longrightarrow \text{Production Orders} \longrightarrow \text{Finished Lots} \longrightarrow \text{Carrier Shipments} \longrightarrow \text{Customer Deliveries}$$

The platform automatically computes downstream recall scopes, tracks corrective interventions (notifications, warehouse quarantines, volume recoveries), audits four mandatory operational anomalies, and computes eight real-time performance evaluation metrics.

---

## 1. Key Capabilities

- **Multi-Echelon Graph Traversal:** Unbroken forward downstream and backward upstream genealogy tracing across all physical transformations and split batches.
- **Dynamic Safety Recall Engine:** Automated isolation of affected finished goods batches, logistics carrier shipments, customer accounts, and total contaminated mass in kilograms.
- **Lifecycle Action Logging:** Immutable event ledger tracking customer safety notices, warehouse quarantine locks, and recovered pallet weights.
- **Pre-Closure Validation:** Prevents closing recall cases while unquarantined stock or unnotified recipient customers remain unresolved.
- **Automated Anomaly Auditing:** Live SQL detection algorithms identifying four mandatory edge cases:
  - `EC-01`: Missing Input Lot (`MISSING_INPUT_LOT`)
  - `EC-02`: Delivery Overrun (`DELIVERY_OVERRUN`)
  - `EC-03`: Missed Downstream Customer (`MISSED_CUSTOMER`)
  - `EC-04`: Inventory Not Quarantined (`INVENTORY_NOT_QUARANTINED`)
- **Strict Ground-Truth Isolation:** Operational detection operates exclusively on runtime transactional tables; ground-truth benchmarks are strictly isolated.
- **Operational Evaluation Suite:** Computes all eight metrics (M-01 to M-08) derived directly from live database records.
- **Deterministic Reproducibility:** Uses fixed seed `20261022` to produce 100% identical outputs and cryptographic checksums across independent runs.

---

## 2. Technology Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (ORM), Alembic, Pydantic V2, Pandas, NumPy, Faker.
- **Database:** PostgreSQL 15+ (production / Docker), SQLite 3 with `StaticPool` (automated test suite).
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide icons.
- **DevOps:** Docker, Docker Compose.

---

## 3. Directory Layout

```
yottaflex-supply-chain-traceability/
├── backend/
│   ├── app/
│   │   ├── config.py              # Pydantic Settings
│   │   ├── database.py            # SQLAlchemy engine & session factory
│   │   ├── main.py                # FastAPI app entrypoint & lifespan
│   │   ├── models/                # 17 SQLAlchemy ORM models
│   │   ├── schemas/               # Pydantic V2 validation schemas
│   │   ├── engine/                # Traversal, recall, exception, & metrics engines
│   │   └── routers/               # 13 FastAPI REST API routers
│   ├── data/
│   │   ├── generators/            # 12-stage deterministic synthetic data generator
│   │   └── exports/               # Exporters for CSV, JSON, SQL seed, Ground Truth
│   ├── migrations/                # Alembic schema migration versions
│   └── tests/                     # Pytest unit & integration test suite
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # 16-section interactive enterprise dashboard
│   │   ├── main.tsx               # React root DOM hydration
│   │   └── index.css              # Tailwind CSS directives
│   ├── package.json               # Frontend dependencies & scripts
│   ├── vite.config.ts             # Vite bundler configuration
│   └── tsconfig.json              # TypeScript configuration
├── docs/                          # Complete 15-document technical suite
├── exports/                       # Full-scale datasets (CSV, JSON, SQL, Ground Truth)
├── docker-compose.yml             # PostgreSQL 15 & Backend services
├── generate_data.py               # Master CLI data generation entrypoint
└── README.md                      # Primary project guide
```

---

## 4. Quick Start Guide

### Step 1: Environment Setup
```bash
# Clone or navigate to the repository
cd yottaflex-supply-chain-traceability

# Setup Python virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 2: Generate Full-Scale Synthetic Data
```bash
# Generate full production scale (500 suppliers, 10k lots, 5k orders, 8k finished lots, 20k deliveries)
python generate_data.py --scale full

# Verify dual-run deterministic reproducibility
python generate_data.py --verify --scale starter
```

### Step 3: Start the Backend REST API Server
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- Interactive ReDoc: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### Step 4: Start the Frontend Operations Console
```bash
cd frontend
npm install
npm run dev
```
Open your browser at [http://localhost:3000](http://localhost:3000) to access the 16-section operations dashboard.

### Step 5: Run Automated Tests
```bash
# Run complete test suite (unit and integration)
python -m pytest backend/tests -v
```

---

## 5. Docker Deployment

Deploy the entire stack with PostgreSQL 15 containerized:
```bash
docker-compose up -d --build
```
This initializes the PostgreSQL database container, applies health checks, starts the FastAPI backend, and exposes the REST API on port `8000`.

---

## 6. Official Documentation Suite

Comprehensive technical documentation is located in the [`docs/`](docs/) directory:

1. [Project Audit](docs/PROJECT_AUDIT.md) — Comprehensive technical audit of existing codebase and corrections.
2. [Project Status](docs/PROJECT_STATUS.md) — Feature status tracking (Completed, Partial, Broken, Missing).
3. [Requirement Traceability Matrix](docs/REQUIREMENT_TRACEABILITY_MATRIX.md) — End-to-end requirement mapping.
4. [Data Dictionary](docs/DATA_DICTIONARY.md) — Exhaustive specification of all 17 tables and columns.
5. [Database Schema](docs/DATABASE_SCHEMA.md) — Relational constraints, check clauses, and indexes.
6. [ER Diagram](docs/ER_DIAGRAM.md) — Mermaid entity-relationship architecture.
7. [Genealogy Design](docs/GENEALOGY_DESIGN.md) — Multi-echelon graph traversal algorithms.
8. [Recall Workflow](docs/RECALL_WORKFLOW.md) — 15-step regulatory recall protocol.
9. [Edge Cases](docs/EDGE_CASES.md) — Specifications for EC-01 through EC-04 anomalies.
10. [Metrics Definitions](docs/METRICS_DEFINITIONS.md) — Mathematical formulas for M-01 through M-08.
11. [Generator Guide](docs/GENERATOR_GUIDE.md) — Deterministic synthetic pipeline guide.
12. [API Documentation](docs/API_DOCUMENTATION.md) — REST endpoint specifications.
13. [Validation Summary](docs/VALIDATION_SUMMARY.md) — Test results and verification evidence.
14. [Source Manifest](docs/SOURCE_MANIFEST.md) — Code inventory and module responsibilities.
## 7. AI Assistance Disclosure

AI tools were used as development assistance during this project.

### Tools Used
- ChatGPT – planning, technical explanations, debugging guidance, code review and validation assistance.
- Antigravity IDE – AI-assisted development and implementation support.

### How AI Was Used
- Understanding requirements and architecture.
- Troubleshooting implementation issues.
- Reviewing data generation and edge-case logic.
- Supporting testing and validation.
- Improving documentation.

### Prompt History
Prompt records for the AI tools used during development are maintained in the `prompt-history/` directory. Any unavailable prompt exports will be disclosed.