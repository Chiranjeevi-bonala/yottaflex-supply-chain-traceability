from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_all_tables
from app.routers import (
    suppliers,
    material_lots,
    products,
    production,
    finished_lots,
    shipments,
    customers,
    deliveries,
    recalls,
    exceptions,
    metrics,
    dashboard,
    exports,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup
    create_all_tables()
    yield

app = FastAPI(
    title="YottaFlex Supply Chain Traceability & Recall Management System",
    description=(
        "Enterprise-grade supply chain traceability and recall management API. "
        "Traces affected material lots through Suppliers -> Raw Material Lots -> "
        "Production Orders -> Finished Lots -> Shipments -> Customer Deliveries. "
        "Automates downstream recall scope calculation, exception detection, "
        "and operational evaluation metrics."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(dashboard.router)
app.include_router(suppliers.router)
app.include_router(material_lots.router)
app.include_router(products.router)
app.include_router(production.router)
app.include_router(finished_lots.router)
app.include_router(shipments.router)
app.include_router(customers.router)
app.include_router(deliveries.router)
app.include_router(recalls.router)
app.include_router(exceptions.router)
app.include_router(metrics.router)
app.include_router(exports.router)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "system": "YottaFlex Traceability System",
        "version": "1.0.0",
        "database": settings.database_url.split("://")[0],
    }

@app.get("/", tags=["System"])
def root():
    return {
        "title": "YottaFlex Supply Chain Traceability & Recall Management System",
        "documentation": "/api/docs",
        "health": "/health",
        "modules": [
            "/api/dashboard/overview",
            "/api/suppliers",
            "/api/material-lots",
            "/api/products",
            "/api/production-orders",
            "/api/finished-lots",
            "/api/shipments",
            "/api/customers",
            "/api/deliveries",
            "/api/recalls",
            "/api/exceptions",
            "/api/metrics",
            "/api/exports/csv",
            "/api/exports/json"
        ]
    }
