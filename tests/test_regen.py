# tests/test_regen.py
from mobius_motor.regen import Metrics, detect_anomalies, regen_cycle

def test_detect_flags_high_error_and_latency():
    m = Metrics(error_rate=0.2, latency_p95_ms=2000.0, utilization=0.95, drift=0.4, theta=0.25)
    det = detect_anomalies(m)
    assert det["anomalies"] is True
    assert det["severity"] >= 1
    assert len(det["reasons"]) >= 1

def test_regen_cycle_returns_final_state_and_params():
    # situație moderată → ar trebui să ducă în Steady (0) sau să rămână stabil
    m = Metrics(error_rate=0.0, latency_p95_ms=800.0, utilization=0.5, drift=0.0, theta=0.5)
    out = regen_cycle(k=1.0, P=1.0, U=5.0, metrics=m)
    assert "final" in out and "k" in out["final"]
    assert out["final"]["state"] in (-1, 0, 1)
