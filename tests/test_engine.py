# tests/test_engine.py
import pytest
from mobius_motor.engine import run_engine, Metrics

def test_engine_wrap_path():
    # theta mare → Arbiter = Wrap (+1)
    m = Metrics(error_rate=0.0, latency_p95_ms=500.0, utilization=0.5, drift=0.0, theta=0.9)
    res = run_engine(k=2.0, P=0.8, U=10.0, theta=0.9, metrics=m, iters=50)
    assert res["arbiter_state"] == 1
    assert "base" in res and res["base"]["mode"] == "wrap"
    assert "balance" in res and "optimize" in res and "entropy" in res

def test_engine_steady_path():
    # theta medie → Arbiter = Steady (0)
    m = Metrics(error_rate=0.01, latency_p95_ms=700.0, utilization=0.6, drift=0.05, theta=0.5)
    res = run_engine(k=1.0, P=1.0, U=5.0, theta=0.5, metrics=m, iters=50)
    assert res["arbiter_state"] == 0
    assert res["base"]["mode"] == "steady"
    assert isinstance(res["entropy"]["avg_value"], float)

def test_engine_unwrap_path():
    # theta mică → Arbiter = Unwrap (-1)
    m = Metrics(error_rate=0.02, latency_p95_ms=1000.0, utilization=0.7, drift=0.2, theta=0.1)
    res = run_engine(k=0.5, P=0.8, U=10.0, theta=0.1, metrics=m, iters=50)
    assert res["arbiter_state"] == -1
    assert res["base"]["mode"] == "unwrap"
    assert res["entropy"]["trials"] == 20
    assert -1 in res["entropy"]["distinct_states"]

def test_engine_regen_integration():
    # Metrics cu anomalii → regen activ
    m = Metrics(error_rate=0.2, latency_p95_ms=2000.0, utilization=0.95, drift=0.4, theta=0.25)
    res = run_engine(k=1.0, P=1.0, U=5.0, theta=0.25, metrics=m, iters=30)
    assert res["regen"] is not None
    assert res["regen"]["detect"]["anomalies"] is True
    assert res["regen"]["final"]["state"] in (-1, 0, 1)
