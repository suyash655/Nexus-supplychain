import pytest
from fastapi.testclient import TestClient
import json
import numpy as np

from app.main import SafeJSONResponse, app

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


def test_safe_json_response_sanitizes_nested_non_finite_numbers():
    response = SafeJSONResponse(
        {
            "metric": float("nan"),
            "nested": {"value": np.float64("inf")},
            "series": [1, np.array([2, np.nan])],
        }
    )

    assert json.loads(response.body) == {
        "metric": None,
        "nested": {"value": None},
        "series": [1, [2.0, None]],
    }
