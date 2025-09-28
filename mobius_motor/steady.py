# Λ-Steady – homeostază (echilibru simplu)
from __future__ import annotations
from typing import Dict

def steady_step(k: float, P: float, U: float, theta: float, iters: int = 100) -> Dict[str, float]:
    """
    Menține sistemul în echilibru:
      - Ajustează parametrii gradual pentru a stabiliza valoarea Λ.
      - Fără expansiune/compresie, doar reglaj fin.
    """
    value = theta
    for _ in range(iters):
        # mică corecție de echilibru
        value += 0.01 * (P - k) - 0.001 * (value - U)

    return {
        "final_value": float(value),
        "params_final": {"k": k, "P": P, "U": U},
        "iters": iters,
        "mode": "steady",
    }
