from .time_formulas import time_wrap, time_steady, time_unwrap
from .arbiter import phi_arbiter

def motor_step(k: float, P: float, U: float, theta: float, low_threshold: float = 0.3, high_threshold: float = 0.7, T1: float = 1.0):
    """
    Executes a single, complete step of the Λ-Möbius engine.

    This is the core function that integrates the decision-making of the
    Arbiter with the mathematical formulas for temporal states.

    Args:
        k (float): The compression/efficiency rate per iteration.
        P (float): The effective parallelism and resource utilization.
        U (float): The external scaling factor (e.g., replicas, services).
        theta (float): The current resilience metric of the system.
        low_threshold (float): The Arbiter's lower bound for the Steady state.
        high_threshold (float): The Arbiter's upper bound for the Steady state.
        T1 (float): The initial cost of detection/boot/regeneration.

    Returns:
        tuple[float, int]: A tuple containing:
            - The calculated Λ-Time value (float).
            - The state chosen by the Arbiter (+1, 0, or -1) (int).
    """
    # 1. Arbiter makes the decision based on system resilience (theta).
    #    Arbiterul ia decizia pe baza rezilienței sistemului (theta).
    state = phi_arbiter(theta, low_threshold, high_threshold)

    # 2. Based on the state, calculate the corresponding Λ-Time.
    #    Pe baza stării, se calculează Λ-Time corespunzător.
    if state == 1:  # Λ-Wrap
        lambda_time = time_wrap(T1, k, P, U)
    elif state == 0:  # Λ-Steady
        lambda_time = time_steady(T1, U)
    else:  # state == -1, Λ-Unwrap
        lambda_time = time_unwrap(T1, k, P, U)
        
    return lambda_time, state
