# mobius_motor/balance.py
# Λ-Balance – menține homeostaza sistemului (PID simplificat)

from __future__ import annotations
from typing import Dict, Tuple
import math

# Refolosim motorul existent
from mobius_motor.core import motor_step

def balance_step(
    k: float,
    P: float,
    U: float,
    theta: float,
    target_value: float,
    kp: float = 0.4,
    ki: float = 0.1,
    kd: float = 0.05,
    iters: int = 100,
) -> Dict[str, object]:
    """
    PID simplificat pentru a stabiliza valoarea Λ în jurul lui `target_value`.
    - kp, ki, kd = coeficienți de control (proporțional, integral, derivativ).
    - iters = câte iterații rulează bucla de stabilizare.
    Returnează ultima valoare și istoricul complet.
    """
    integral = 0.0
    prev_err = 0.0
    history: list[Tuple[float, float, int]] = []

    for t in range(1, iters + 1):
        val, st = motor_step(k=k, P=P, U=U, theta=theta)
        err = target_value - val
        integral += err
        deriv = err - prev_err

        adjust = kp * err + ki * integral + kd * deriv

        # reglăm doar P (paralelism) pentru simplitate
        P = max(0.1, P + adjust)

        prev_err = err
        history.append((val, P, st))

        # stabilizat suficient de aproape
        if abs(err) < 1e-4:
            break

    return {
        "final_value": float(val),
        "final_state": int(st),
        "params_final": {"k": k, "P": P, "U": U},
        "error": float(err),
        "iters": t,
        "history": history,
        "target": target_value,
    }
