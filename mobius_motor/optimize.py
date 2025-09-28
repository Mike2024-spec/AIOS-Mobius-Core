# mobius_motor/optimize.py
import math
from dataclasses import dataclass
from typing import Dict, Tuple, Literal, Optional

State = Literal[-1, 0, 1]  # -1=Λ-Unwrap, 0=Λ-Steady, 1=Λ-Wrap

@dataclass(frozen=True)
class OptimizeResult:
    params_opt: Tuple[float, float, float]  # (k, P, U)
    final_value: float                      # Λ-Time
    final_state: State
    iterations: int
    converged: bool
    mode: str

def _phi_arbiter(theta: float, low: float, high: float) -> State:
    if theta >= high:
        return 1
    if theta >= low:
        return 0
    return -1

def _lambda_time(k: float, P: float, U: float, theta: float,
                 T1: float = 1.0, low: float = 0.33, high: float = 0.66) -> Tuple[float, State]:
    # Safety clamps
    k = max(1e-6, float(k))
    P = max(1e-6, float(P))
    U = max(1.000001, float(U))  # ensure log(U) > 0
    logU = math.log(U)
    state = _phi_arbiter(theta, low, high)
    kP = k * P

    if state == 1:  # Λ-Wrap (compression)
        if kP <= 1.0:
            # Physically inconsistent for Wrap; degrade to Steady
            return (T1 * logU, 0)
        denom = 1.0 - 1.0 / kP
        denom = max(1e-9, denom)
        return (T1 * logU / denom, 1)

    if state == 0:  # Λ-Steady
        return (T1 * logU, 0)

    # state == -1 → Λ-Unwrap (expansion)
    if abs(kP) < 1.0:
        denom = 1.0 - kP
        denom = max(1e-9, denom)
        return (T1 * logU / denom, -1)
    # Divergent series → truncate to N terms
    N = 12
    acc = 0.0
    term = T1 * logU
    factor = kP
    for i in range(N):
        acc += term * (factor ** i)
    return (acc, -1)

def motor_step_eval(k: float, P: float, U: float, theta: float,
                    T1: float = 1.0, low: float = 0.33, high: float = 0.66) -> Tuple[float, State]:
    """Helper used by optimizer and external callers."""
    return _lambda_time(k, P, U, theta, T1=T1, low=low, high=high)

def lambda_optimize(
    initial_guess: Tuple[float, float, float] = (1.0, 1.0, 5.0),
    theta: float = 0.5,
    mode: Literal["value", "state"] = "value",
    target: Optional[float] = None,
    desired_state: Optional[State] = None,
    bounds: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]] = ((0.1, 5.0), (0.1, 1.0), (1.001, 100.0)),
    T1: float = 1.0,
    low: float = 0.33,
    high: float = 0.66,
    max_iter: int = 500,
    tol: float = 1e-4,
) -> Dict[str, object]:
    """
    Deterministic coordinate search with step decay.
    - mode='value': minimize |Λ - target|
    - mode='state': enforce desired_state in {-1,0,1} with heavy penalty if unmet
    """
    if mode == "value" and target is None:
        raise ValueError("target must be provided for mode='value'")
    if mode == "state" and desired_state is None:
        raise ValueError("desired_state must be provided for mode='state'")

    (kmin, kmax), (pmin, pmax), (umin, umax) = bounds
    k, P, U = initial_guess
    k = min(max(k, kmin), kmax)
    P = min(max(P, pmin), pmax)
    U = min(max(U, umin), umax)

    step_k, step_P, step_U = 0.5, 0.2, 5.0

    def objective(kv: float, Pv: float, Uv: float) -> Tuple[float, float, State]:
        val, st = _lambda_time(kv, Pv, Uv, theta, T1=T1, low=low, high=high)
        if mode == "value":
            score = abs(val - float(target))  # distance to target
        else:
            # Heavy penalty if wrong state
            penalty = 0.0 if st == desired_state else 1e6
            # Secondary objective: for Wrap favor kP>1, for Unwrap favor kP<1, for Steady favor |kP-1| close to 0
            kP = kv * Pv
            if desired_state == 1:
                shape = max(0.0, 1.0 - (kP - 1.0))  # encourage >1
            elif desired_state == -1:
                shape = max(0.0, kP - 0.999)
            else:
                shape = abs(kP - 1.0)
            score = penalty + shape + 1e-6 * abs(val)
        return score, val, st

    best_score, best_val, best_state = objective(k, P, U)
    best_k, best_P, best_U = k, P, U
    it = 0
    converged = False

    while it < max_iter:
        improved = False
        it += 1
        candidates = [
            (best_k + step_k, best_P, best_U),
            (best_k - step_k, best_P, best_U),
            (best_k, best_P + step_P, best_U),
            (best_k, best_P - step_P, best_U),
            (best_k, best_P, best_U + step_U),
            (best_k, best_P, best_U - step_U),
        ]
        for ck, cP, cU in candidates:
            ck = min(max(ck, kmin), kmax)
            cP = min(max(cP, pmin), pmax)
            cU = min(max(cU, umin), umax)
            sc, v, st = objective(ck, cP, cU)
            if sc + 1e-12 < best_score:
                best_score, best_val, best_state = sc, v, st
                best_k, best_P, best_U = ck, cP, cU
                improved = True

        if not improved:
            # decay steps
            step_k *= 0.5
            step_P *= 0.5
            step_U *= 0.5
            if max(step_k, step_P, step_U) < tol:
                converged = True
                break

    return OptimizeResult(
        params_opt=(best_k, best_P, best_U),
        final_value=best_val,
        final_state=best_state,
        iterations=it,
        converged=converged,
        mode=mode,
    ).__dict__
