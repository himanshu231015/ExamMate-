"""Tests for system health and documentation availability."""

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "RGPV ExamMate"
    assert "documentation" in data


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"


def test_openapi_docs_accessible(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert "/api/v1/auth/login" in data["paths"]
    assert "/api/v1/pyqs/search" in data["paths"]
