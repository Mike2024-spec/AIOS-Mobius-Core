# mobius_motor/optimize.py
# Λ-Optimize – căutare parametri (fără dependențe externe)
from __future__ import annotations
import math
from typing import Dict, Tuple

# Refolosim motorul existent
from mobius_motor.core import motor_step  # -> (value, state)

Bounds = Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]

def _clip(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x

def lambda_optimize(
    initial_guess: Tuple[float, float, float],
    theta: float,
    mode: str = "value",           # "value" sau "state"
    target: float | None = None,   # necesar pentru mode="value"
    desired_state: int | None = None,  # +1 wrap, 0 steady, -1 unwrap
    bounds: Bounds = ((0.1, 5.0), (0.1, 2.0), (1.0, 100.0)),  # k, P, U
    max_iters: int = 2000,
    tol: float = 1e-6,
    shrink: float = 0.5,
) -> Dict[str, object]:
    """
    Caută (k, P, U) astfel încât:
      - mode="value": Λ ≈ target  (cu penalizare dacă desired_state e setat)
      - mode="state": starea == desired_state (minimizând Λ ca tie-break)
    Metodă: coordinate descent determinist, fără numpy/scipy.
    """
    if mode not in {"value", "state"}:
        raise ValueError("mode must be 'value' or 'state'")
    if mode == "value" and target is None:
        raise ValueError("target is required for mode='value'")

    (k_lo, k_hi), (p_lo, p_hi), (u_lo, u_hi) = bounds

    # Inițializare
    k, P, U = initial_guess
    k = _clip(k, k_lo, k_hi)
    P = _clip(P, p_lo, p_hi)
    U = _clip(U, u_lo, u_hi)

    def objective(k: float, P: float, U: float):
        val, st = motor_step(k=k, P=P, U=U, theta=theta)
        if mode == "value":
            loss = abs(val - float(target))
            if desired_state is not None and st != desired_state:
                loss += 1000.0  # penalizare dură pentru stare greșită
        else:  # mode == "state"
            if desired_state is None:
                raise ValueError("desired_state is required for mode='state'")
            loss = 0.0 if st == desired_state else 1000.0
            # tie-break: preferăm Λ mai mic
            loss += 0.001 * abs(val)
        return loss, val, st

    best_loss, best_val, best_st = objective(k, P, U)
    best = (k, P, U)

    step_k = 0.25 * (k_hi - k_lo)
    step_P = 0.25 * (p_hi - p_lo)
    step_U = 0.25 * (u_hi - u_lo)

    for it in range(1, max_iters + 1):
        improved = False
        for i, (lo, hi, step) in enumerate(
            ((k_lo, k_hi, step_k), (p_lo, p_hi, step_P), (u_lo, u_hi, step_U))
        ):
            for direction in (+1, -1):
                kk, PP, UU = best
                trial = [kk, PP, UU]
                trial[i] = _clip(trial[i] + direction * step, lo, hi)
                loss, val, st = objective(trial[0], trial[1], trial[2])
                if loss + tol < best_loss:
                    best_loss, best_val, best_st = loss, val, st
                    best = (trial[0], trial[1], trial[2])
                    improved = True
        # micșorăm pașii
        step_k *= shrink
        step_P *= shrink
        step_U *= shrink
        if not improved and max(step_k, step_P, step_U) < tol:
            break

    k, P, U = best
    return {
        "params_opt": {"k": k, "P": P, "U": U},
        "final_value": float(best_val),
        "final_state": int(best_st),
        "loss": float(best_loss),
        "iters": it,
        "theta": float(theta),
        "mode": mode,
        "target": None if target is None else float(target),
        "desired_state": None if desired_state is None else int(desired_state),
        "bounds": {"k": [k_lo, k_hi], "P": [p_lo, p_hi], "U": [u_lo, u_hi]},
    }

# alias Unicode, dacă dorești import ca λ_optimize
λ_optimize = lambda_optimize
