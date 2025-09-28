# tests/test_balance.py
import pytest
from mobius_motor.balance import balance_step

def test_balance_converges():
    res = balance_step(
        k=1.0, P=1.0, U=5.0, theta=0.6,
        target_value=10.0,
        iters=200
    )
    # structura corectă
    assert "final_value" in res
    assert "params_final" in res
    assert "history" in res

    # valoarea finală ≈ 10
    assert abs(res["final_value"] - 10.0) < 2.0

    # parametrii finali sunt pozitivi
    pf = res["params_final"]
    assert pf["k"] > 0
    assert pf["P"] > 0
    assert pf["U"] > 0

    # history nu e gol
    assert len(res["history"]) > 0
