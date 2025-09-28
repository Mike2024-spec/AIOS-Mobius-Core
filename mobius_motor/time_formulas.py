import numpy as np

# Constante de siguranță pentru a preveni diviziunea cu zero sau instabilitatea.
# Safety constants to prevent division by zero or instability.
KP_STABILITY_FACTOR = 0.9999 
LOG_U_STABILITY_FACTOR = 1e-9

def time_wrap(T1, k, P, U):
    """
    Calculates Λ-Time for the Wrap state (compression).
    Formula: T1 * log(U) / (1 - 1/(k*P))
    Used when the system is highly resilient and can handle higher processing density.
    """
    # Asigură k*P este suficient de mare pentru a evita instabilitatea aproape de 1.
    # Ensure k*P is large enough to avoid instability near 1.
    kp_product = k * P
    if kp_product <= 1:
        # În starea Wrap, k*P trebuie să fie > 1. Dacă nu, este o condiție de eroare.
        # In Wrap state, k*P must be > 1. If not, it's an error condition.
        return np.inf  # Returnează infinit pentru a semnala o stare invalidă.

    # Previne log(0) sau log(1)
    # Prevents log(0) or log(1)
    safe_U = U if U > 1 else 1 + LOG_U_STABILITY_FACTOR

    denominator = 1 - (1 / kp_product)
    
    return (T1 * np.log(safe_U)) / denominator

def time_steady(T1, U):
    """
    Calculates Λ-Time for the Steady state (stagnation).
    Formula: T1 * log(U)
    Used for stable, homeostatic operation.
    """
    # Previne log(0) sau log(1)
    # Prevents log(0) or log(1)
    safe_U = U if U > 1 else 1 + LOG_U_STABILITY_FACTOR
    return T1 * np.log(safe_U)

def time_unwrap(T1, k, P, U, max_iter=100):
    """
    Calculates Λ-Time for the Unwrap state (expansion) using a geometric series.
    Formula: Sum(T1 * (k*P)^i * log(U))
    Converges to T1*log(U) / (1 - k*P) if |k*P| < 1.
    Used for controlled stress testing or deep analysis.
    """
    kp_product = k * P
    
    # Previne log(0) sau log(1)
    # Prevents log(0) or log(1)
    safe_U = U if U > 1 else 1 + LOG_U_STABILITY_FACTOR
    log_U_term = np.log(safe_U)

    # Dacă |k*P| >= 1, seria diverge. O oprim la un prag pentru a preveni infinitul.
    # If |k*P| >= 1, the series diverges. We cap it to prevent infinite loops.
    if abs(kp_product) >= 1:
        # Calculăm o sumă parțială mare ca penalizare pentru divergență.
        # We calculate a large partial sum as a penalty for divergence.
        total = 0
        for i in range(max_iter):
            total += T1 * (kp_product ** i) * log_U_term
        return total

    # Dacă |k*P| < 1, seria converge și putem folosi formula directă.
    # If |k*P| < 1, the series converges, and we can use the direct formula.
    return (T1 * log_U_term) / (1 - kp_product)
