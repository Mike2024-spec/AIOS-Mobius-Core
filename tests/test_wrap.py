import pytest
from mobius_motor.wrap import wrap_step

def test_wrap_structure():
    res = wrap_step(k=1.0, P=1.0, U=5.0, theta=10.0, iters=50)
    assert "final_value" in res
    assert "params_final" in res
    assert res["mode"] == "wrap"

def test_wrap_decay():
    res = wrap_step(k=1.0, P=1.0, U=5.0, theta=10.0, iters=200)
    # compresia trebuie să ducă la valori mai mici decât theta inițial
    assert res["final_value"] < 10.0
