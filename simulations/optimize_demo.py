# simulations/optimize_demo.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mobius_motor.optimize import lambda_optimize

def main():
    print("--- Λ-OPTIMIZE DEMO ---")

    # Caz 1: țintă pe valoare (Λ ≈ 12) în regim mediu
    res1 = lambda_optimize(
        initial_guess=(1.0, 1.0, 5.0),
        theta=0.45,
        mode="value",
        target=12.0,
        desired_state=0,  # preferăm Steady dacă e posibil
    )
    print("[CASE 1]", res1)

    # Caz 2: țintă pe stare (forțează Λ-Wrap)
    res2 = lambda_optimize(
        initial_guess=(0.8, 0.6, 10.0),
        theta=0.85,
        mode="state",
        desired_state=+1,
    )
    print("[CASE 2]", res2)

    # Caz 3: țintă pe stare (forțează Λ-Unwrap)
    res3 = lambda_optimize(
        initial_guess=(1.2, 0.8, 8.0),
        theta=0.15,
        mode="state",
        desired_state=-1,
    )
    print("[CASE 3]", res3)

    print("--- DONE ---")

if __name__ == "__main__":
    main()
