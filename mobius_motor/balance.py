# mobius_motor/balance.py
# Λ-Balance – menținere homeostază (PID-like control pentru valoarea Λ)

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
    lr: float = 0.05,   # rate de învățare
) -> Dict[str, object]:
    """
    Ajustează parametrii (k, P, U) iterativ astfel încât Λ ≈ target_value.
    Folosește un control simplu tip gradient descent/PID.

    Returnează:
      - final_value: valoarea Λ obținută
      - params_final: dict cu k, P, U finale
      - history: listă de tuple (val, st)
    """
    history: List[Tuple[float, int]] = []
    best_val, best_params = None, (k, P, U)

    for _ in range(iters):
        val, st = motor_step(k=k, P=P, U=U, theta=theta)
        history.append((val, st))

        # dacă este cea mai bună valoare până acum
        if best_val is None or abs(val - target_value) < abs(best_val - target_value):
            best_val = val
            best_params = (k, P, U)

        # eroare față de țintă
        error = target_value - val

        # update simplu PID-like → corecție proporțională
        k += lr * error * 0.1
        P += lr * error * 0.05
        U += lr * error * 0.01

        # limite minime (nu vrem valori negative sau zero)
        k = max(0.1, k)
        P = max(0.1, P)
        U = max(1.0, U)

    k, P, U = best_params
    return {
        "final_value": float(best_val),
        "params_final": {"k": k, "P": P, "U": U},
        "history": history,
    }
