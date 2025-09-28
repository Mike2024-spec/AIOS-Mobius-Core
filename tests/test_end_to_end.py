# tests/test_end_to_end.py
import math
import json
import subprocess
import sys
from fastapi.testclient import TestClient

from mobius_motor.engine import run_engine, Metrics
from aios.api import app

client = TestClient(app)


def test_core_and_engine_consistency():
    m = Metrics(error_rate=0.0, latency_p95_ms=800.0, utilization=0.5, drift=0.0, theta=0.9)
    out = run_engine(k=2.0, P=0.8, U=10.0, theta=0.9, metrics=m)
    # Arbiter: theta=0.9 → Wrap
    assert out["arbiter_state"] == 1
    assert "base" in out and "final_value" in out["base"]
    assert out["base"]["mode"] == "wrap"


def test_api_and_core_match():
    payload = {"k": 2.0, "P": 0.8, "U": 10.0, "theta": 0.9}
    r = client.post("/step", json=payload)
    assert r.status_code == 200
    data = r.json()
    # API trebuie să raporteze Wrap
    assert data["state"] == 1
    expected = (1.0 * math.log(10.0)) / (1 - 1/(payload["k"]*payload["P"]))
    assert abs(data["value"] - expected) < 1e-6


def test_cli_and_api_consistency(tmp_path):
    cli_cmd = [
        sys.executable, "-m", "mobius_motor.cli", "step",
        "--k", "2.0", "--P", "0.8", "--U", "10.0", "--theta", "0.9"
    ]
    result = subprocess.run(cli_cmd, capture_output=True, text=True)
    assert result.returncode == 0
    cli_out = json.loads(result.stdout)
    # CLI trebuie să raporteze Wrap
    assert cli_out["state"] == 1

    # API check
    r = client.post("/step", json={"k": 2.0, "P": 0.8, "U": 10.0, "theta": 0.9})
    data = r.json()
    assert data["state"] == cli_out["state"]
    assert abs(data["value"] - cli_out["value"]) < 1e-6
