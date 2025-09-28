# tests/test_balance.py
import pytest
from mobius_motor.balance import balance_step

def test_balance_converges():
    res = balance_step(
        k=1.0, P=1.0, U=5.0, theta=0.6,
        target_value=10.0,
        iters=200
    )
    # verificăm că a returnat structura corectă
    assert "final_value" in res
    assert "params_final" in res
    assert "history" in res
    # valoarea finală să fie aproape de țintă
    assert abs(res["final_value"] - 10.0) < 2.0
    # stare validă: -1, 0 sau +1
    assert res["final_state"] in (-1, 0, 1)
