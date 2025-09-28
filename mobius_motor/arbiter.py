def phi_arbiter(theta: float, low_threshold: float, high_threshold: float) -> int:
    """
    The Λ-Arbiter (Lambda-Arbiter). The reptilian brain of the engine.

    This function acts as a simple, fast decision-maker based on the system's
    resilience metric (Theta - Θ). It chooses the appropriate temporal state.

    Args:
        theta (float): The current resilience value of the system.
        low_threshold (float): The lower bound for the Steady state.
        high_threshold (float): The upper bound for the Steady state.

    Returns:
        int: The state decision:
             +1 for Λ-Wrap (compression, high resilience)
              0 for Λ-Steady (homeostasis, normal resilience)
             -1 for Λ-Unwrap (expansion, low resilience)
    """
    if not low_threshold < high_threshold:
        raise ValueError("The low_threshold must be strictly less than the high_threshold.")

    if theta >= high_threshold:
        # Resilience is high. The system can handle temporal compression.
        # Engage Λ-Wrap.
        return 1
    
    if low_threshold <= theta < high_threshold:
        # Resilience is normal. Maintain stability.
        # Engage Λ-Steady.
        return 0
    
    # theta < low_threshold
    # Resilience is low. Expand time for analysis or controlled stress.
    # Engage Λ-Unwrap.
    return -1
