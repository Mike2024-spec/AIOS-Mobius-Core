# Λ-Arbiter – unica definiție
def phi_arbiter(theta: float, low_threshold: float, high_threshold: float) -> int:
    """
    Arbiterul decide starea sistemului:
      +1 → Λ-Wrap (compression)
       0 → Λ-Steady (homeostasis)
      -1 → Λ-Unwrap (expansion)
    """
    if not low_threshold < high_threshold:
        raise ValueError("low_threshold must be < high_threshold")

    if theta >= high_threshold:
        return 1
    if low_threshold <= theta < high_threshold:
        return 0
    return -1
