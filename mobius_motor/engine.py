# mobius_motor/engine.py
# Λ-Möbius Engine Orchestrator – flux unificat

from typing import Dict, Any
from mobius_motor.arbiter import phi_arbiter
from mobius_motor.core import motor_step
from mobius_motor.wrap import wrap_step
from mobius_motor.steady import steady_step
from mobius_motor.unwrap import unwrap_step
from mobius_motor.regen import regen_cycle, Metrics
from mobius_motor.balance import balance_step
from mobius_motor.optimize import lambda_optimize
from mobius_motor.entropy import entropy_step

# praguri globale – se pot muta într-un config separat
THETA_LOW = 0.3
THETA_HIGH = 0.7

def run_engine(
    k: float,
    P: float,
    U: float,
    theta: float,
    metrics: Metrics | None = None,
    iters: int = 100,
) -> Dict[str, Any]:
    """
    Orchestrator complet pentru Λ-Möbius Engine.
    Rulează Arbiter → modul de bază → regen/balance/optimize → entropy.
    """
    # 1. Arbiter decide starea
    state = phi_arbiter(theta, THETA_LOW, THETA_HIGH)

    # 2. Rulăm modulul corespunzător
    if state == 1:
        base = wrap_step(k, P, U, theta, iters=iters)
    elif state == 0:
        base = steady_step(k, P, U, theta, iters=iters)
    else:
        base = unwrap_step(k, P, U, theta, iters=iters)

    # 3. Dacă avem metrice, rulăm regen
    regen_out = None
    if metrics:
        regen_out = regen_cycle(k, P, U, metrics)

    # 4. Balance simplu spre valoarea de bază
    balance_out = balance_step(k, P, U, theta, target_value=base["final_value"])

    # 5. Optimize pentru a verifica convergența
    opt_out = lambda_optimize(
        initial_guess=(k, P, U),
        theta=theta,
        mode="state",
        desired_state=state,
    )

    # 6. Entropy test pentru stres
    entropy_out = entropy_step(k, P, U, theta, trials=20, perturb=0.15)

    # 7. Returnăm rezultatul complet
    return {
        "arbiter_state": state,
        "base": base,
        "regen": regen_out,
        "balance": balance_out,
        "optimize": opt_out,
        "entropy": entropy_out,
    }

if __name__ == "__main__":
    # demo rapid
    m = Metrics(error_rate=0.01, latency_p95_ms=800.0, utilization=0.5, drift=0.1, theta=0.6)
    out = run_engine(k=1.0, P=1.0, U=5.0, theta=0.6, metrics=m)
    import json
    print(json.dumps(out, indent=2))
