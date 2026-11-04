"""The Schmidt-form model: parametrisation, decomposition, invariants and edge cases."""
import cmath
import math
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import schmidt
import tools

ROOT2 = 1 / 2 ** 0.5
PURE = {'00': [1, 0, 0, 0], '11': [0, 0, 0, 1],
        'phi+': [ROOT2, 0, 0, ROOT2], 'phi-': [ROOT2, 0, 0, -ROOT2],
        'psi+': [0, ROOT2, ROOT2, 0], 'psi-': [0, ROOT2, -ROOT2, 0]}


def same_up_to_phase(first, second, places=9):
    overlap = sum(complex(a).conjugate() * complex(b) for a, b in zip(first, second))
    if abs(overlap) < 1e-12:
        return False
    phase = overlap / abs(overlap)
    return all(abs(complex(b) - phase * complex(a)) < 10 ** -places for a, b in zip(first, second))


def sigma_apply(axis, state):
    """(n̂·σ)|ψ⟩, so a test can check that an eigenstate really is one."""
    x, y, z = schmidt.unit(axis)
    alpha, beta = state
    return (z * alpha + (x - 1j * y) * beta, (x + 1j * y) * alpha - z * beta)


def random_state(rng):
    amplitudes = [complex(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(4)]
    norm = math.sqrt(sum(abs(value) ** 2 for value in amplitudes))
    return [value / norm for value in amplitudes]


def apply_local(state, first, second):
    """(U_a ⊗ U_b)|ψ⟩ for two 2×2 matrices given as nested tuples."""
    c = [[state[0], state[1]], [state[2], state[3]]]
    mixed = [[sum(first[j][a] * c[a][b] * second[k][b] for a in (0, 1) for b in (0, 1))
              for k in (0, 1)] for j in (0, 1)]
    return [mixed[0][0], mixed[0][1], mixed[1][0], mixed[1][1]]


class SchmidtModelTests(unittest.TestCase):
    def test_eigenstates_are_orthonormal_eigenstates_of_the_axis(self):
        for axis in ((0, 0, 1), (1, 0, 0), (0, 1, 0), (0, 0, -1),
                     (1 / 3 ** 0.5, 1 / 3 ** 0.5, 1 / 3 ** 0.5), (-0.3, 0.5, 0.81)):
            plus, minus = schmidt.eigenstates(axis)
            self.assertAlmostEqual(sum(abs(value) ** 2 for value in plus), 1, places=12)
            self.assertAlmostEqual(sum(abs(value) ** 2 for value in minus), 1, places=12)
            self.assertAlmostEqual(abs(plus[0].conjugate() * minus[0]
                                       + plus[1].conjugate() * minus[1]), 0, places=12)
            for sign, state in ((1, plus), (-1, minus)):
                for got, want in zip(sigma_apply(axis, state), state):
                    self.assertAlmostEqual(got, sign * want, places=12)

    def test_schmidt_state_is_normalised_and_has_the_declared_amplitudes(self):
        for theta in (0, 17, 30, 45):
            for polar, azimuth, chi in ((0, 0, 0), (90, 0, 60), (55, 305, 250), (180, 0, 180)):
                axis = schmidt.axis_from_angles(polar, azimuth)
                state = schmidt.schmidt_state(theta, axis, axis, chi)
                self.assertAlmostEqual(sum(abs(value) ** 2 for value in state), 1, places=12)
        state = schmidt.schmidt_state(30, (0, 0, 1), (0, 0, 1), 60)
        for got, want in zip(state, (math.cos(math.radians(30)), 0, 0,
                                     cmath.exp(1j * math.radians(60)) * math.sin(math.radians(30)))):
            self.assertAlmostEqual(got, want, places=12)

    def test_known_states_have_the_expected_form(self):
        cases = {'00': (0.0, (0, 0, 1), (0, 0, 1)),
                 '11': (0.0, (0, 0, -1), (0, 0, -1)),
                 'phi+': (45.0, (0, 0, 1), (0, 0, 1)),
                 'phi-': (45.0, (0, 0, 1), (0, 0, 1)),
                 'psi+': (45.0, (0, 0, 1), (0, 0, -1)),
                 'psi-': (45.0, (0, 0, 1), (0, 0, -1))}
        for name, (theta, axis_a, axis_b) in cases.items():
            form = schmidt.schmidt_form(PURE[name])
            self.assertAlmostEqual(form.theta_deg, theta, places=9, msg=name)
            for got, want in zip(form.axis_a, axis_a):
                self.assertAlmostEqual(got, want, places=9, msg=name)
            for got, want in zip(form.axis_b, axis_b):
                self.assertAlmostEqual(got, want, places=9, msg=name)
            self.assertTrue(same_up_to_phase(
                schmidt.schmidt_state(form.theta_deg, form.axis_a, form.axis_b, form.chi_deg),
                PURE[name]), name)

    def test_bell_states_are_maximally_entangled_with_the_right_relative_phase(self):
        phases = {'phi+': 0.0, 'phi-': 180.0}
        for name, want in phases.items():
            form = schmidt.schmidt_form(PURE[name])
            self.assertAlmostEqual(form.theta_deg, 45, places=9)
            self.assertAlmostEqual(form.chi_deg, want, places=9)
            self.assertAlmostEqual(schmidt.concurrence(PURE[name]), 1, places=12)
            self.assertAlmostEqual(schmidt.entanglement_entropy(PURE[name]), 1, places=12)

    def test_schmidt_form_round_trips_random_states(self):
        rng = random.Random(20261103)
        for _ in range(40):
            state = random_state(rng)
            form = schmidt.schmidt_form(state)
            rebuilt = schmidt.schmidt_state(form.theta_deg, form.axis_a, form.axis_b, form.chi_deg)
            self.assertTrue(same_up_to_phase(rebuilt, state),
                            f'round trip failed for {state} → {form}')

    def test_parameters_round_trip_through_the_state(self):
        rng = random.Random(7)
        for _ in range(40):
            theta = rng.uniform(2, 43)
            axis_a = schmidt.unit((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)))
            axis_b = schmidt.unit((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)))
            chi = rng.uniform(0, 360)
            form = schmidt.schmidt_form(schmidt.schmidt_state(theta, axis_a, axis_b, chi))
            self.assertAlmostEqual(form.theta_deg, theta, places=8)
            for got, want in zip(form.axis_a, axis_a):
                self.assertAlmostEqual(got, want, places=8)
            for got, want in zip(form.axis_b, axis_b):
                self.assertAlmostEqual(got, want, places=8)
            self.assertAlmostEqual(form.chi_deg, chi, places=8)

    def test_the_schmidt_vectors_carry_the_singular_values(self):
        rng = random.Random(17)
        for _ in range(20):
            state = random_state(rng)
            first, second, lead, partner, amplitudes = schmidt.decompose(state)
            other_a = (-lead[1].conjugate(), lead[0].conjugate())
            other_b = (-partner[1].conjugate(), partner[0].conjugate())
            self.assertAlmostEqual(abs(schmidt.overlap(amplitudes, lead, partner)), first, places=9)
            self.assertAlmostEqual(abs(schmidt.overlap(amplitudes, other_a, other_b)), second, places=9)
            self.assertAlmostEqual(abs(schmidt.overlap(amplitudes, lead, other_b)), 0, places=9)
            self.assertAlmostEqual(abs(schmidt.overlap(amplitudes, other_a, partner)), 0, places=9)

    def test_coefficients_are_ordered_and_sum_to_one(self):
        rng = random.Random(11)
        for _ in range(30):
            state = random_state(rng)
            first, second = schmidt.schmidt_coefficients(state)
            self.assertGreaterEqual(first, second - 1e-12)
            self.assertAlmostEqual(first + second, 1, places=9)
            form = schmidt.schmidt_form(state)
            self.assertAlmostEqual(first, form.coefficients[0], places=9)
            self.assertAlmostEqual(second, form.coefficients[1], places=9)

    def test_concurrence_and_entropy_follow_the_schmidt_angle(self):
        for theta in (0, 10, 22.5, 30, 45):
            state = schmidt.schmidt_state(theta, (0, 0, 1), (1, 0, 0), 25)
            weight = math.cos(math.radians(theta)) ** 2
            self.assertAlmostEqual(schmidt.concurrence(state), math.sin(math.radians(2 * theta)), places=12)
            want = sum(-value * math.log2(value) for value in (weight, 1 - weight) if value > 0)
            self.assertAlmostEqual(schmidt.entanglement_entropy(state), want, places=12)

    def test_reduced_states_have_the_schmidt_axes_and_shrink_with_entanglement(self):
        rng = random.Random(5)
        for _ in range(20):
            theta = rng.uniform(0, 45)
            axis_a = schmidt.unit((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)))
            axis_b = schmidt.unit((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)))
            state = schmidt.schmidt_state(theta, axis_a, axis_b, rng.uniform(0, 360))
            scale = math.cos(math.radians(2 * theta))
            for got, want in zip(schmidt.reduced_bloch(state, 0), axis_a):
                self.assertAlmostEqual(got, scale * want, places=9)
            for got, want in zip(schmidt.reduced_bloch(state, 1), axis_b):
                self.assertAlmostEqual(got, scale * want, places=9)

    def test_relative_phase_changes_the_state_but_not_the_invariants(self):
        axes = ((90, 0), (35, 200))
        first = schmidt.state_from_angles(28, *axes[0], *axes[1], 0)
        second = schmidt.state_from_angles(28, *axes[0], *axes[1], 90)
        self.assertFalse(same_up_to_phase(first, second))
        for got, want in zip(schmidt.schmidt_coefficients(first), schmidt.schmidt_coefficients(second)):
            self.assertAlmostEqual(got, want, places=12)
        for quantity in (schmidt.concurrence, schmidt.entanglement_entropy):
            self.assertAlmostEqual(quantity(first), quantity(second), places=12)
        for qubit in (0, 1):
            for got, want in zip(schmidt.reduced_bloch(first, qubit), schmidt.reduced_bloch(second, qubit)):
                self.assertAlmostEqual(got, want, places=12)
        self.assertAlmostEqual(schmidt.schmidt_form(second).chi_deg, 90, places=9)

    def test_the_phase_is_what_two_qubit_interference_sees(self):
        # In the computational basis the relative phase is the phase of c00 conj(c11) against
        # c01 conj(c10); a global phase cancels from the ratio.
        state = schmidt.schmidt_state(33, (0, 0, 1), (0, 0, 1), 70)
        coherence = state[0].conjugate() * state[3]      # e^{iχ} cos θ sin θ for the z basis
        self.assertAlmostEqual(cmath.phase(coherence) % (2 * math.pi), math.radians(70) % (2 * math.pi), places=9)
        for global_phase in (0.4, 2.1):
            turned = [value * cmath.exp(1j * global_phase) for value in state]
            self.assertAlmostEqual(schmidt.schmidt_form(turned).chi_deg,
                                   schmidt.schmidt_form(state).chi_deg, places=9)

    def test_schmidt_angle_is_invariant_under_local_unitaries(self):
        hadamard = ((ROOT2, ROOT2), (ROOT2, -ROOT2))
        phase = ((1, 0), (0, 1j))
        flip = ((0, 1), (1, 0))
        identity = ((1, 0), (0, 1))
        rng = random.Random(3)
        for _ in range(12):
            state = random_state(rng)
            want = schmidt.schmidt_form(state).theta_deg
            want_concurrence = schmidt.concurrence(state)
            for first, second in ((hadamard, identity), (identity, phase),
                                  (flip, phase), (hadamard, hadamard), (phase, flip)):
                moved = apply_local(state, first, second)
                self.assertAlmostEqual(schmidt.schmidt_form(moved).theta_deg, want, places=8)
                self.assertAlmostEqual(schmidt.concurrence(moved), want_concurrence, places=9)

    def test_product_and_maximal_entanglement_degeneracies(self):
        # θ = 0: the second branch has zero weight, so χ is meaningless and the state is product.
        for chi in (0, 123):
            state = schmidt.schmidt_state(0, (1, 0, 0), (0, 1, 0), chi)
            self.assertTrue(same_up_to_phase(state,
                                             schmidt.schmidt_state(0, (1, 0, 0), (0, 1, 0), 0)))
            self.assertAlmostEqual(schmidt.concurrence(state), 0, places=12)
        # θ = π/4: the Schmidt basis is not unique. The same Phi+ appears in the z and x bases,
        # while the y basis pair spans a different corner and builds Phi- instead.
        for axis in ((0, 0, 1), (1, 0, 0)):
            state = schmidt.schmidt_state(45, axis, axis, 0)
            self.assertTrue(same_up_to_phase(state, PURE['phi+']), axis)
            self.assertAlmostEqual(schmidt.concurrence(state), 1, places=12)
        self.assertTrue(same_up_to_phase(schmidt.schmidt_state(45, (0, 1, 0), (0, 1, 0), 0),
                                         PURE['phi-']))

    def test_axis_helpers_agree_with_the_bloch_sphere_module(self):
        for polar in (0, 17, 90, 143, 180):
            for azimuth in (0, 45, 90, 217, 359):
                self.assertEqual(schmidt.axis_from_angles(polar, azimuth),
                                 tools.rotation_axis(polar, azimuth))
                axis = schmidt.axis_from_angles(polar, azimuth)
                got_polar, got_azimuth = schmidt.angles_from_axis(axis)
                self.assertAlmostEqual(got_polar, polar, places=9)
                if 0 < polar < 180:
                    self.assertAlmostEqual(got_azimuth, azimuth, places=9)

    def test_state_from_angles_matches_the_vector_constructor(self):
        for theta, polar_a, azimuth_a, polar_b, azimuth_b, chi in ((25, 90, 0, 0, 0, 40),
                                                                  (45, 55, 305, 120, 44, 300),
                                                                  (5, 180, 0, 90, 270, 0)):
            self.assertTrue(same_up_to_phase(
                schmidt.state_from_angles(theta, polar_a, azimuth_a, polar_b, azimuth_b, chi),
                schmidt.schmidt_state(theta, schmidt.axis_from_angles(polar_a, azimuth_a),
                                      schmidt.axis_from_angles(polar_b, azimuth_b), chi)))

    def test_rejects_states_that_are_not_normalised(self):
        for state in ([1, 0, 0, 0.1], [0, 0, 0, 0], [1, 0, 0]):
            with self.assertRaises(ValueError):
                schmidt.schmidt_form(state)
        for axis in ((0, 0, 0),):
            with self.assertRaises(ValueError):
                schmidt.unit(axis)


if __name__ == '__main__':
    unittest.main()
