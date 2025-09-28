# tests/test_entropy.py
from mobius_motor.entropy import entropy_step

def test_entropy_runs():
    res = entropy_step(k=1.0, P=1.0, U=5.0, theta=0.5, trials=20, perturb=0.2)

    # Structura returnată
    assert "avg_value" in res
    assert "min_value" in res
    assert "max_value" in res
    assert "distinct_states" in res
    assert res["trials"] == 20

    # Consistență numerică
    assert res["min_value"] <= res["avg_value"] <= res["max_value"]
    assert isinstance(res["distinct_states"], list)
