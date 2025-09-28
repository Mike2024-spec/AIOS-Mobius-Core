# Adăugăm calea rădăcinii proiectului pentru a putea importa motorul.
# This allows us to import the engine from the parent directory.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mobius_motor.core import motor_step

def run_simulation():
    """
    Runs a simple simulation to demonstrate the Λ-Möbius engine's behavior
    in different resilience scenarios.
    """
    print("--- INITIATING AIOS-MOBIUS-CORE SIMULATION ---")
    print("="*50)

    # --- Scenariul 1: Reziliență Ridicată (High Resilience) ---
    # Ne așteptăm ca Arbiterul să aleagă starea Λ-Wrap.
    # We expect the Arbiter to choose the Λ-Wrap state.
    print("[SCENARIO 1: HIGH RESILIENCE]")
    theta_high = 0.85
    k_high, P_high, U_high = 2.5, 0.7, 15.0 # k*P = 1.75 > 1
    
    value, state = motor_step(k=k_high, P=P_high, U=U_high, theta=theta_high)
    
    state_desc = {1: "Λ-Wrap (Compression)", 0: "Λ-Steady", -1: "Λ-Unwrap"}.get(state)
    print(f"  Resilience (Theta): {theta_high}")
    print(f"  Arbiter Decision:   State {state} -> {state_desc}")
    print(f"  Calculated Λ-Time:  {value:.4f}")
    print("-"*50)


    # --- Scenariul 2: Homeostază (Homeostasis) ---
    # Ne așteptăm ca Arbiterul să aleagă starea Λ-Steady.
    # We expect the Arbiter to choose the Λ-Steady state.
    print("[SCENARIO 2: HOMEOSTASIS]")
    theta_mid = 0.5
    k_mid, P_mid, U_mid = 1.0, 1.0, 15.0
    
    value, state = motor_step(k=k_mid, P=P_mid, U=U_mid, theta=theta_mid)
    
    state_desc = {1: "Λ-Wrap", 0: "Λ-Steady (Equilibrium)", -1: "Λ-Unwrap"}.get(state)
    print(f"  Resilience (Theta): {theta_mid}")
    print(f"  Arbiter Decision:   State {state} -> {state_desc}")
    print(f"  Calculated Λ-Time:  {value:.4f}")
    print("-"*50)


    # --- Scenariul 3: Reziliență Scăzută (Low Resilience) ---
    # Ne așteptăm ca Arbiterul să aleagă starea Λ-Unwrap.
    # We expect the Arbiter to choose the Λ-Unwrap state.
    print("[SCENARIO 3: LOW RESILIENCE]")
    theta_low = 0.15
    k_low, P_low, U_low = 0.8, 0.6, 15.0 # k*P = 0.48 < 1
    
    value, state = motor_step(k=k_low, P=P_low, U=U_low, theta=theta_low)
    
    state_desc = {1: "Λ-Wrap", 0: "Λ-Steady", -1: "Λ-Unwrap (Expansion)"}.get(state)
    print(f"  Resilience (Theta): {theta_low}")
    print(f"  Arbiter Decision:   State {state} -> {state_desc}")
    print(f"  Calculated Λ-Time:  {value:.4f}")
    print("="*50)
    print("--- SIMULATION COMPLETE ---")


if __name__ == '__main__':
    run_simulation()
