from fastapi.testclient import TestClient

def test_health_and_root(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    res = client.get("/")
    assert res.status_code == 200
    assert "documentation" in res.json()

def test_dashboard_overview(client: TestClient):
    res = client.get("/api/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    assert "volumes" in data
    assert "recalls" in data
    assert "key_metrics" in data

def test_all_entity_endpoints(client: TestClient):
    assert client.get("/api/suppliers").status_code == 200
    assert client.get("/api/material-lots").status_code == 200
    assert client.get("/api/products").status_code == 200
    assert client.get("/api/production-orders").status_code == 200
    assert client.get("/api/production/orders").status_code == 200
    assert client.get("/api/finished-lots").status_code == 200
    assert client.get("/api/shipments").status_code == 200
    assert client.get("/api/customers").status_code == 200
    assert client.get("/api/deliveries").status_code == 200
    assert client.get("/api/recalls").status_code == 200
    assert client.get("/api/exceptions").status_code == 200
    assert client.get("/api/exceptions/detected").status_code == 200
    assert client.get("/api/exceptions/audit-report").status_code == 200
    assert client.get("/api/metrics").status_code == 200
    assert client.get("/api/metrics/recall").status_code == 200
    assert client.get("/api/metrics/exceptions").status_code == 200

def test_export_endpoints(client: TestClient):
    res_json = client.get("/api/exports/json?entity=suppliers")
    assert res_json.status_code == 200
    assert "records" in res_json.json()

    res_csv = client.get("/api/exports/csv?entity=suppliers")
    assert res_csv.status_code == 200
