import pytest
from mobius_motor.steady import steady_step

def test_steady_structure():
    res = steady_step(k=1.0, P=1.0, U=5.0, theta=2.0, iters=50)
    assert "final_value" in res
    assert "params_final" in res
    assert res["mode"] == "steady"

def test_steady_converges():
    res = steady_step(k=1.0, P=1.0, U=5.0, theta=2.0, iters=200)
    # verificăm că valoarea finală nu explodează
    assert abs(res["final_value"]) < 100.0
