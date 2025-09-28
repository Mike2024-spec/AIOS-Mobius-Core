import unittest
import numpy as np

# Importăm componentele motorului pentru a le testa
# We import the engine components to test them
from mobius_motor.time_formulas import time_wrap, time_steady, time_unwrap
from mobius_motor.arbiter import phi_arbiter
from mobius_motor.core import motor_step

class TestMobiusEngine(unittest.TestCase):

    def test_arbiter_states(self):
        """Validates the Λ-Arbiter's decision logic."""
        # Testează dacă arbiterul returnează starea corectă pentru fiecare interval de theta.
        # Tests if the arbiter returns the correct state for each theta interval.
        self.assertEqual(phi_arbiter(theta=0.9, low_threshold=0.3, high_threshold=0.7), 1, "Should be in Wrap state")
        self.assertEqual(phi_arbiter(theta=0.5, low_threshold=0.3, high_threshold=0.7), 0, "Should be in Steady state")
        self.assertEqual(phi_arbiter(theta=0.1, low_threshold=0.3, high_threshold=0.7), -1, "Should be in Unwrap state")
        
        # Testează cazurile limită (edge cases).
        # Test the edge cases.
        self.assertEqual(phi_arbiter(theta=0.7, low_threshold=0.3, high_threshold=0.7), 1, "Upper boundary should trigger Wrap")
        self.assertEqual(phi_arbiter(theta=0.3, low_threshold=0.3, high_threshold=0.7), 0, "Lower boundary should be in Steady")

    def test_time_formulas_basic(self):
        """Validates the basic calculations of the time formulas."""
        # Valori de test simple și previzibile.
        # Simple and predictable test values.
        T1, k, P, U = 1.0, 2.0, 0.6, 10.0 # k*P = 1.2 > 1
        
        # Wrap: 1 * log(10) / (1 - 1/1.2) = 2.302 / (1 - 0.833) = 2.302 / 0.166... ≈ 13.81
        self.assertAlmostEqual(time_wrap(T1, k, P, U), (np.log(10) / (1 - 1/1.2)), places=2)
        
        # Steady: 1 * log(10) ≈ 2.302
        self.assertAlmostEqual(time_steady(T1, U), np.log(10), places=2)

        # Unwrap: k*P = 0.4 < 1. 1 * log(10) / (1 - 0.4) = 2.302 / 0.6 ≈ 3.83
        k_unwrap, P_unwrap = 0.8, 0.5
        self.assertAlmostEqual(time_unwrap(T1, k_unwrap, P_unwrap, U), (np.log(10) / (1 - 0.4)), places=2)

    def test_wrap_invalid_state(self):
        """Ensures time_wrap handles invalid k*P product correctly."""
        # Testează cazul în care k*P <= 1, ceea ce ar trebui să returneze infinit.
        # Tests the case where k*P <= 1, which should return infinity.
        self.assertEqual(time_wrap(T1=1.0, k=1.0, P=1.0, U=10.0), np.inf, "k*P = 1 should be an invalid state")
        self.assertEqual(time_wrap(T1=1.0, k=0.5, P=1.0, U=10.0), np.inf, "k*P < 1 should be an invalid state")

    def test_core_integration(self):
        """Tests the full integration in motor_step."""
        # Verifică dacă motor_step alege starea corectă și returnează valoarea corespunzătoare.
        # Verifies that motor_step chooses the correct state and returns the corresponding value.
        
        # Scenariu pentru Wrap
        val_wrap, state_wrap = motor_step(k=2.0, P=0.8, U=10.0, theta=0.9)
        self.assertEqual(state_wrap, 1)
        self.assertAlmostEqual(val_wrap, time_wrap(1.0, 2.0, 0.8, 10.0))

        # Scenariu pentru Steady
        val_steady, state_steady = motor_step(k=2.0, P=0.8, U=10.0, theta=0.5)
        self.assertEqual(state_steady, 0)
        self.assertAlmostEqual(val_steady, time_steady(1.0, 10.0))

        # Scenariu pentru Unwrap
        val_unwrap, state_unwrap = motor_step(k=0.5, P=0.8, U=10.0, theta=0.1)
        self.assertEqual(state_unwrap, -1)
        self.assertAlmostEqual(val_unwrap, time_unwrap(1.0, 0.5, 0.8, 10.0))


# Această parte permite rularea testelor direct din linia de comandă.
# This part allows running the tests directly from the command line.
if __name__ == '__main__':
    unittest.main()
