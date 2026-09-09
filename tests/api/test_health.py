from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_app_startup() -> None:
    assert app.title == "Sutra API"
    assert app.version == "0.1.0"


def test_health_check_status_code() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_check_response_body() -> None:
    response = client.get("/api/v1/health")
    assert response.json() == {
        "status": "ok",
        "service": "sutra-api",
    }
