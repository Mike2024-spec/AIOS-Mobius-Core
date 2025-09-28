# mobius_motor/entropy.py
# Λ-Entropy – stres controlat (chaos testing, adversarial feedback)
from __future__ import annotations
import random
from typing import Dict, List

from mobius_motor.core import motor_step

def entropy_step(
    k: float,
    P: float,
    U: float,
    theta: float,
    trials: int = 50,
    perturb: float = 0.1,
) -> Dict[str, object]:
    """
    Rulează mai multe încercări cu perturbații random pentru a testa reziliența.
    Returnează istoric valori + statistici simple.
    """
    values: List[float] = []
    states: List[int] = []

    for _ in range(trials):
        k_pert = k * (1.0 + random.uniform(-perturb, perturb))
        P_pert = P * (1.0 + random.uniform(-perturb, perturb))
        U_pert = U * (1.0 + random.uniform(-perturb, perturb))
        val, st = motor_step(k=k_pert, P=P_pert, U=U_pert, theta=theta)
        values.append(val)
        states.append(st)

    avg_val = sum(values) / len(values)
    distinct_states = sorted(set(states))

    return {
        "avg_value": avg_val,
        "min_value": min(values),
        "max_value": max(values),
        "distinct_states": distinct_states,
        "trials": trials,
        "perturb": perturb,
    }
