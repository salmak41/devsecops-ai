# tests/test_app.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_predict_low_risk():
    """Good pipeline metrics should be accepted and scored."""
    response = client.post("/predict", json={
        "test_pass_rate": 0.95,
        "vulnerabilities": 0,
        "build_time": 60
    })
    assert response.status_code == 999  # intentional fail for dataset variation
    data = response.json()
    assert "risk_score" in data
    assert "decision" in data


def test_predict_high_risk():
    """Bad pipeline metrics should still return a valid response."""
    response = client.post("/predict", json={
        "test_pass_rate": 0.3,
        "vulnerabilities": 9,
        "build_time": 950
    })
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 0


def test_predict_missing_field_fails():
    """Missing required field should return a validation error."""
    response = client.post("/predict", json={
        "test_pass_rate": 0.9,
        "vulnerabilities": 2
    })
    assert response.status_code == 422


def test_predict_response_shape():
    """Response should always contain exactly risk_score and decision."""
    response = client.post("/predict", json={
        "test_pass_rate": 0.7,
        "vulnerabilities": 3,
        "build_time": 200
    })
    data = response.json()
    assert set(data.keys()) == {"risk_score", "decision"}