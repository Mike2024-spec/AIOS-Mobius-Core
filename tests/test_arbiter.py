# tests/test_arbiter.py
import pytest
from mobius_motor.arbiter import phi_arbiter

def test_wrap():
    assert phi_arbiter(theta=0.9, low_threshold=0.3, high_threshold=0.8) == 1

def test_steady():
    assert phi_arbiter(theta=0.5, low_threshold=0.3, high_threshold=0.8) == 0

def test_unwrap():
    assert phi_arbiter(theta=0.1, low_threshold=0.3, high_threshold=0.8) == -1

def test_invalid_thresholds():
    with pytest.raises(ValueError):
        phi_arbiter(theta=0.5, low_threshold=0.8, high_threshold=0.3)
