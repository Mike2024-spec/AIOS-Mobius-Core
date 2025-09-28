# tests/test_api.py
import math
from fastapi.testclient import TestClient

from aios.api import app  # asigură-te că există aios/__init__.py
client = TestClient(app)

def test_step_wrap():
    payload = {"k": 2.0, "P": 0.8, "U": 10.0, "theta": 0.9}  # k*P=1.6>1, theta>=0.7 → Wrap
    r = client.post("/step", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["state"] == 1
    expected = (1.0 * math.log(10.0)) / (1 - 1/(payload["k"]*payload["P"]))
    assert math.isfinite(data["value"])
    assert abs(data["value"] - expected) < 1e-6

def test_step_steady():
    payload = {"k": 2.0, "P": 0.8, "U": 10.0, "theta": 0.5}  # 0.3<=theta<0.7 → Steady
    r = client.post("/step", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["state"] == 0
    expected = 1.0 * math.log(10.0)
    assert abs(data["value"] - expected) < 1e-6

def test_step_unwrap():
    payload = {"k": 0.5, "P": 0.5, "U": 10.0, "theta": 0.1}  # k*P=0.25<1, theta<0.3 → Unwrap
    r = client.post("/step", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["state"] == -1
    expected = (1.0 * math.log(10.0)) / (1 - (payload["k"]*payload["P"]))
    assert abs(data["value"] - expected) < 1e-6

def test_optimize_value_steady_target():
    # Țintă realizabilă în Steady (log U ≈ 3 → U≈20.085 în bounds [1,100])
    payload = {
        "k": 1.0, "P": 1.0, "U": 5.0,
        "theta": 0.45,
        "mode": "value",
        "target": 3.0,
        "desired_state": 0
    }
    r = client.post("/optimize", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "params_opt" in data and "final_value" in data and "final_state" in data
    assert data["final_state"] == 0
    assert abs(data["final_value"] - 3.0) < 0.1  # toleranță mică

def test_optimize_force_wrap_state():
    payload = {
        "k": 0.8, "P": 0.6, "U": 10.0,
        "theta": 0.85,
        "mode": "state",
        "desired_state": 1
    }
    r = client.post("/optimize", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["final_state"] == 1
