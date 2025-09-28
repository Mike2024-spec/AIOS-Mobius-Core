# Λ-Unwrap – expansiune (divergență controlată)
from __future__ import annotations
from typing import Dict

def unwrap_step(k: float, P: float, U: float, theta: float, iters: int = 100) -> Dict[str, float]:
    """
    Expansiune controlată:
      - Sistemul crește valoarea Λ gradual.
      - Simulează dilatarea parametrilor în timp.
    """
    value = theta
    history = []
    for _ in range(iters):
        value = value * (1 + 0.01 * P) + 0.001 * U - 0.0005 * k
        history.append(value)

    return {
        "final_value": float(value),
        "params_final": {"k": k, "P": P, "U": U},
        "iters": iters,
        "history": history,
        "mode": "unwrap",
    }
