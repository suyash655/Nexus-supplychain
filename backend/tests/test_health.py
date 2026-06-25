import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_check():
    """
    Smoke test to ensure the application imports cleanly and the root endpoint
    is available. Prevents CI pipeline from failing entirely on missing tests.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    # The application starts up even if some engines are mocked/degraded
    assert data["status"] == "online"
