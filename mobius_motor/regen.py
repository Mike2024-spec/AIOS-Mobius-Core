# mobius_motor/regen.py
"""
Λ-Regen: Detect → Quarantine → Improve → Reinvest
Implementare minimă, deterministă, fără dependențe externe.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

from mobius_motor.core import motor_step
from mobius_motor.optimize import lambda_optimize
from mobius_motor.arbiter import phi_arbiter


# ==========
# 1) INPUT METRICS + PRAGURI
# ==========
@dataclass(frozen=True)
class Metrics:
    error_rate: float          # 0..1
    latency_p95_ms: float      # ms
    utilization: float         # 0..1
    drift: float               # 0..1 (model/data drift)
    theta: float               # reziliență curentă (0..1)

# praguri simple; pot fi adjustate ulterior
ER_HIGH = 0.05        # >5% erori
LAT_HIGH = 1500.0     # p95 > 1.5s
UTIL_HIGH = 0.90      # >90% utilizare
DRIFT_HIGH = 0.30     # >30% drift
THETA_LOW = 0.30
THETA_HIGH = 0.70


# ==========
# 2) DETECT
# ==========
def detect_anomalies(m: Metrics) -> Dict[str, object]:
    reasons: List[str] = []
    if m.error_rate > ER_HIGH:        reasons.append(f"error_rate>{ER_HIGH}")
    if m.latency_p95_ms > LAT_HIGH:   reasons.append(f"latency_p95_ms>{LAT_HIGH}")
    if m.utilization > UTIL_HIGH:     reasons.append(f"utilization>{UTIL_HIGH}")
    if m.drift > DRIFT_HIGH:          reasons.append(f"drift>{DRIFT_HIGH}")
    if m.theta < THETA_LOW:           reasons.append(f"theta<{THETA_LOW}")

    severity = 0
    if reasons:
        # severitate = 1 (mediu) sau 2 (ridicat)
        bad = sum([
            m.error_rate > ER_HIGH,
            m.latency_p95_ms > LAT_HIGH,
            m.utilization > UTIL_HIGH,
            m.drift > DRIFT_HIGH,
            m.theta < THETA_LOW,
        ])
        severity = 1 if bad == 1 else 2

    return {"anomalies": bool(reasons), "reasons": reasons, "severity": severity}


# ==========
# 3) QUARANTINE (plan de izolare de urgență)
# ==========
def quarantine_plan(severity: int) -> Dict[str, object]:
    if severity == 0:
        return {"active": False, "actions": []}
    actions: List[str] = []
    # plan conservativ, fără efecte secundare reale (doar recomandări)
    if severity >= 1:
        actions.append("route_away_20_percent")      # scade încărcarea
        actions.append("freeze_new_deploys")         # blochează rollout
    if severity >= 2:
        actions.append("disable_suspect_feature")    # izolează zona suspectă
        actions.append("scale_safe_pool_up")         # scalare pe noduri sănătoase
    return {"active": True, "actions": actions}


# ==========
# 4) IMPROVE (reparație: aduce sistemul în Steady)
# ==========
def improve_params(k: float, P: float, U: float, theta: float) -> Dict[str, object]:
    """
    Țintim starea 0 (Λ-Steady): stabilizare. Folosim optimizerul intern.
    """
    res = lambda_optimize(
        initial_guess=(k, P, U),
        theta=theta,
        mode="state",
        desired_state=0,     # vrem homeostază
    )
    return res  # conține params_opt, final_value, final_state etc.


# ==========
# 5) REINVEST (distribuție simplă a câștigurilor)
# ==========
def reinvest_policy() -> Dict[str, float]:
    # Politică de bază – se poate înlocui ulterior cu una dinamică.
    return {
        "observability": 0.40,  # loguri/metrici mai bune → scade T1
        "redundancy":    0.30,  # MTTR mai mic
        "optimization":  0.30,  # crește k · P
    }


# ==========
# 6) CICLUL COMPLET
# ==========
def regen_cycle(
    k: float, P: float, U: float, metrics: Metrics, T1: float = 1.0
) -> Dict[str, object]:
    """
    Rulează D→Q→I→R pentru un pas.
    Returnează:
      - detect, quarantine, improve, reinvest
      - final (parametri + Λ + stare)
    """
    # Detect
    det = detect_anomalies(metrics)

    # Quarantine
    q = quarantine_plan(det["severity"])

    # Improve (doar dacă avem probleme sau arbiterul nu e Steady)
    state_now = phi_arbiter(metrics.theta, THETA_LOW, THETA_HIGH)
    if det["severity"] > 0 or state_now != 0:
        imp = improve_params(k, P, U, metrics.theta)
        k2, P2, U2 = (
            imp["params_opt"]["k"],
            imp["params_opt"]["P"],
            imp["params_opt"]["U"],
        )
    else:
        imp = {"params_opt": {"k": k, "P": P, "U": U}, "final_state": state_now}
        k2, P2, U2 = k, P, U

    # Reinvest (static acum)
    reinv = reinvest_policy()

    # Valoarea finală
    val, st = motor_step(k2, P2, U2, metrics.theta, THETA_LOW, THETA_HIGH, T1)

    return {
        "detect": det,
        "quarantine": q,
        "improve": imp,
        "reinvest": reinv,
        "final": {"k": k2, "P": P2, "U": U2, "lambda": float(val), "state": int(st)},
    }
