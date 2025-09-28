import pytest
from mobius_motor.unwrap import unwrap_step

def test_unwrap_structure():
    res = unwrap_step(k=1.0, P=1.0, U=5.0, theta=1.0, iters=50)
    assert "final_value" in res
    assert "params_final" in res
    assert res["mode"] == "unwrap"

def test_unwrap_growth():
    res = unwrap_step(k=1.0, P=1.0, U=5.0, theta=1.0, iters=200)
    # expansiunea trebuie să ducă la valori mai mari decât theta inițial
    assert res["final_value"] > 1.0
