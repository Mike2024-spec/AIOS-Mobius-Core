# mobius_motor/balance.py
# Λ-Balance – homeostază, convergență spre valoarea țintă

from __future__ import annotations
from typing import Dict, List, Tuple
from mobius_motor.core import motor_step

def balance_step(
    k: float,
    P: float,
    U: float,
    theta: float,
    target_value: float,
    iters: int = 200,
    lr: float = 0.05,
) -> Dict[str, object]:
    """
    Ajustează parametrii (k, P, U) astfel încât Λ_time să se apropie de target_value.
    Metodă: gradient descent simplificat (determinist).
    """
    history: List[Tuple[float, float, float, float]] = []
    best_params = (k, P, U)
    best_val, _ = motor_step(k, P, U, theta)
    best_loss = abs(best_val - target_value)

    for _ in range(iters):
        val, st = motor_step(k, P, U, theta)
        loss = abs(val - target_value)
        history.append((k, P, U, val))

        if loss < best_loss:
            best_loss = loss
            best_val = val
            best_params = (k, P, U)

        # update simplu: mișcare proporțională cu eroarea
        if val < target_value:
            U *= (1 + lr)
            P *= (1 + lr / 2)
        else:
            U *= (1 - lr)
            P *= (1 - lr / 2)

        k = max(0.1, k * (1 + 0.01 * (target_value - val)))

    return {
        "params_final": {"k": best_params[0], "P": best_params[1], "U": best_params[2]},
        "final_value": best_val,
        "final_state": int(st),
        "loss": best_loss,
        "history": history,
    }
