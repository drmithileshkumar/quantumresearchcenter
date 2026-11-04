"""The Schmidt form of a two-qubit pure state: the mathematical model for the Schmidt visualizer.

Every pure state of two qubits can be written, up to one global phase, as

    |ψ⟩ = cos θ |+n̂_a⟩|+n̂_b⟩ + e^{iχ} sin θ |−n̂_a⟩|−n̂_b⟩,

where |±n̂⟩ are the ±1 eigenstates of n̂·σ, so {|+n̂⟩, |−n̂⟩} is an orthonormal basis
of one qubit for each of the two directions n̂_a and n̂_b. The two coefficients are the
singular values of the 2 × 2 amplitude matrix c[j][k] = ⟨j k|ψ⟩, written c = U S V†:

    c = cos θ |+n̂_a⟩⟨+n̂_b| + e^{iχ} sin θ |−n̂_a⟩⟨−n̂_b|.

The parameters are

    θ        the Schmidt angle, 0 ≤ θ ≤ π/4, with Schmidt coefficients cos²θ ≥ sin²θ,
    n̂_a      the Schmidt axis of the first qubit (two angles on its Bloch sphere),
    n̂_b      the Schmidt axis of the second qubit (two angles),
    χ        the relative phase between the two Schmidt terms.

Six real parameters: exactly the dimension of the two-qubit pure-state space after the
global phase is removed. Each one has a direct meaning.

* θ measures entanglement. θ = 0 is a product state |+n̂_a⟩|+n̂_b⟩; θ = π/4 is maximally
  entangled. The concurrence is sin 2θ and the entanglement entropy is H₂(cos²θ).
* n̂_a and n̂_b are the local Schmidt frames. The reduced state of the first qubit is
  ρ_a = ½(I + cos 2θ n̂_a·σ), so its Bloch vector is cos 2θ n̂_a: the local arrows shrink
  along the Schmidt axes while staying antipodal within each qubit's basis.
* χ is a relative phase between the two branches. It leaves the Schmidt coefficients and
  both reduced states untouched, so it is invisible on either local Bloch sphere; it is
  what a two-qubit interference experiment measures.

Degeneracies the visualizer has to respect: at θ = 0 the phase χ is meaningless (one
branch has zero weight), and at θ = π/4 the decomposition is not unique — the same
maximally entangled state has many Schmidt bases, for example
Φ⁺ = (|00⟩ + |11⟩)/√2 = (|++⟩ + |−−⟩)/√2.

Phase convention: |±n̂⟩ above is the standard parametrisation, whose phase jumps as n̂
crosses a pole (the azimuth stops meaning anything there, so χ is defined only relative
to it). A drawing that only shows the local Bloch vectors and Schmidt weights does not
see that jump; a drawing of the computational amplitudes should carry the basis phases
continuously while a pointer moves the axis.

States are flat amplitude lists [c00, c01, c10, c11] in the computational basis, the same
convention as the rest of `scripts/tools.py`.
"""
from typing import NamedTuple

import cmath
import math

ZERO = 1e-9


class SchmidtForm(NamedTuple):
    """A two-qubit pure state in Schmidt form, with the coefficients in decreasing order."""

    theta_deg: float
    axis_a: tuple
    axis_b: tuple
    chi_deg: float

    @property
    def coefficients(self):
        """The Schmidt coefficients (cos²θ, sin²θ), larger first."""
        cos = math.cos(math.radians(self.theta_deg))
        return (cos * cos, 1.0 - cos * cos)


def axis_from_angles(polar_deg, azimuth_deg):
    """The unit Bloch vector n̂ at a polar angle and an azimuth, both in degrees.

    The convention matches `tools.rotation_axis`: the polar angle is measured from +z and the
    azimuth counter-clockwise from +x.
    """
    polar, azimuth = math.radians(polar_deg), math.radians(azimuth_deg)
    return (math.sin(polar) * math.cos(azimuth), math.sin(polar) * math.sin(azimuth), math.cos(polar))


def angles_from_axis(axis):
    """The polar angle and azimuth of a non-zero vector, in degrees (azimuth in [0, 360))."""
    x, y, z = unit(axis)
    polar = math.degrees(math.acos(max(-1.0, min(1.0, z))))
    azimuth = math.degrees(math.atan2(y, x)) % 360 if math.hypot(x, y) > ZERO else 0.0
    return (polar, azimuth)


def unit(vector):
    """A vector scaled to length one; a zero vector is rejected because it names no direction."""
    length = math.sqrt(sum(value * value for value in vector))
    if length < ZERO:
        raise ValueError('A Schmidt axis must be a non-zero vector.')
    return tuple(value / length for value in vector)


def eigenstates(axis):
    """The +1 and −1 eigenstates of n̂·σ, as complex amplitude pairs.

    With n̂ at polar angle α and azimuth φ this is
    |+n̂⟩ = (cos α/2, e^{iφ} sin α/2) and |−n̂⟩ = (sin α/2, −e^{iφ} cos α/2).
    """
    x, y, z = unit(axis)
    polar = math.acos(max(-1.0, min(1.0, z)))
    azimuth = math.atan2(y, x) if math.hypot(x, y) > ZERO else 0.0
    half, turn = polar / 2, cmath.exp(1j * azimuth)
    return ((math.cos(half), turn * math.sin(half)),
            (math.sin(half), -turn * math.cos(half)))


def _tensor(first, second):
    return (first[0] * second[0], first[0] * second[1], first[1] * second[0], first[1] * second[1])


def _normalised(pair):
    length = math.hypot(abs(pair[0]), abs(pair[1]))
    if length < ZERO:
        raise ValueError('Cannot normalise a zero amplitude pair.')
    return (pair[0] / length, pair[1] / length)


def _validate(state):
    if len(state) != 4:
        raise ValueError('A two-qubit state needs four amplitudes, ordered [c00, c01, c10, c11].')
    amplitudes = tuple(complex(value) for value in state)
    norm = sum(abs(value) ** 2 for value in amplitudes)
    if abs(norm - 1) > 1e-6:
        raise ValueError('A two-qubit state must be normalised; got |ψ|² = ' + f'{norm:.6f}.')
    return amplitudes


def schmidt_state(theta_deg, axis_a, axis_b, chi_deg):
    """|ψ⟩ = cos θ |+a⟩|+b⟩ + e^{iχ} sin θ |−a⟩|−b⟩, flattened to [c00, c01, c10, c11]."""
    theta, phase = math.radians(theta_deg), cmath.exp(1j * math.radians(chi_deg))
    plus_a, minus_a = eigenstates(axis_a)
    plus_b, minus_b = eigenstates(axis_b)
    first, second = _tensor(plus_a, plus_b), _tensor(minus_a, minus_b)
    return tuple(math.cos(theta) * first[index] + phase * math.sin(theta) * second[index]
                 for index in range(4))


def state_from_angles(theta_deg, polar_a, azimuth_a, polar_b, azimuth_b, chi_deg):
    """The Schmidt state whose axes are given by their two angles each."""
    return schmidt_state(theta_deg, axis_from_angles(polar_a, azimuth_a),
                         axis_from_angles(polar_b, azimuth_b), chi_deg)


def schmidt_coefficients(state):
    """The squared singular values of the amplitude matrix, larger first."""
    first, second, *_ = decompose(state)
    return (first * first, second * second)


def decompose(state):
    """Singular values of the amplitude matrix and the Schmidt basis of each qubit.

    Returns (s0, s1, |a0⟩, |b0⟩, amplitudes) with s0 ≥ s1 and |a0⟩, |b0⟩ unit vectors. Only
    the leading basis vectors are needed to fix both axes: |a1⟩ and |b1⟩ are their orthogonal
    complements, up to the phases that the Schmidt decomposition fixes.
    """
    c = _validate(state)
    c00, c01, c10, c11 = c
    rows = (abs(c00) ** 2 + abs(c01) ** 2, abs(c10) ** 2 + abs(c11) ** 2)
    mixing = c00 * c10.conjugate() + c01 * c11.conjugate()
    mean = (rows[0] + rows[1]) / 2
    spread = math.hypot((rows[0] - rows[1]) / 2, abs(mixing))
    first = math.sqrt(max(0.0, mean + spread))
    # s0² s1² = det(c c†): more accurate than mean − spread when the state is nearly a product.
    determinant = max(0.0, rows[0] * rows[1] - abs(mixing) ** 2)
    second = math.sqrt(determinant) / first if first > ZERO else 0.0
    if abs(mixing) > ZERO:
        # Eigenvector of c c† for the larger singular value: the leading ket of the first qubit.
        # Both forms are eigenvectors; take the larger one so a degenerate matrix stays well scaled.
        candidates = ((mixing, first * first - rows[0]), (first * first - rows[1], mixing.conjugate()))
        lead = _normalised(max(candidates, key=lambda pair: abs(pair[0]) ** 2 + abs(pair[1]) ** 2))
    else:
        lead = (1.0 + 0j, 0j) if rows[0] >= rows[1] else (0j, 1.0 + 0j)
    # c = U S V† writes c[j][k] = Σ s_i a_i[j] b_i[k] only once the right singular vector is
    # conjugated, so b_0 = conj(c† a_0) / s_0.
    right = (c00.conjugate() * lead[0] + c10.conjugate() * lead[1],
             c01.conjugate() * lead[0] + c11.conjugate() * lead[1])
    partner = _normalised((right[0].conjugate(), right[1].conjugate()))
    return first, second, lead, partner, c


def bloch_vector(amplitudes):
    """The Bloch vector of a pure single-qubit state given by its two amplitudes."""
    alpha, beta = amplitudes
    product = alpha.conjugate() * beta
    return (2 * product.real, 2 * product.imag, abs(alpha) ** 2 - abs(beta) ** 2)


def schmidt_form(state):
    """The Schmidt parameters of a normalised state, with the coefficients in decreasing order."""
    first, second, lead, partner, amplitudes = decompose(state)
    theta = math.degrees(math.atan2(second, first))
    axis_a, axis_b = bloch_vector(lead), bloch_vector(partner)
    phase = 0.0
    if second > ZERO:
        plus_a, minus_a = eigenstates(axis_a)
        plus_b, minus_b = eigenstates(axis_b)
        weight_plus = overlap(amplitudes, plus_a, plus_b)
        weight_minus = overlap(amplitudes, minus_a, minus_b)
        if abs(weight_plus) > ZERO and abs(weight_minus) > ZERO:
            phase = math.degrees(cmath.phase(weight_minus / weight_plus)) % 360
    return SchmidtForm(theta, axis_a, axis_b, phase)


def overlap(amplitudes, first, second):
    """⟨first second|ψ⟩ for the flat amplitude list: how much of the state lies in |first⟩|second⟩."""
    return (first[0].conjugate() * second[0].conjugate() * amplitudes[0]
            + first[0].conjugate() * second[1].conjugate() * amplitudes[1]
            + first[1].conjugate() * second[0].conjugate() * amplitudes[2]
            + first[1].conjugate() * second[1].conjugate() * amplitudes[3])


def concurrence(state):
    """2 s0 s1, which is sin 2θ: 0 for a product state and 1 at maximal entanglement."""
    first, second, *_ = decompose(state)
    return 2 * first * second


def entanglement_entropy(state):
    """The von Neumann entropy of either reduced state, in bits."""
    return sum(-weight * math.log2(weight) for weight in schmidt_coefficients(state) if weight > ZERO)


def reduced_bloch(state, qubit=0):
    """The Bloch vector of the reduced state of one qubit, which is cos 2θ n̂ of that qubit."""
    c = _validate(state)
    if qubit == 0:
        rho01 = c[0] * c[2].conjugate() + c[1] * c[3].conjugate()
        diagonal = (abs(c[0]) ** 2 + abs(c[1]) ** 2, abs(c[2]) ** 2 + abs(c[3]) ** 2)
    elif qubit == 1:
        rho01 = c[0] * c[1].conjugate() + c[2] * c[3].conjugate()
        diagonal = (abs(c[0]) ** 2 + abs(c[2]) ** 2, abs(c[1]) ** 2 + abs(c[3]) ** 2)
    else:
        raise ValueError('A two-qubit state has qubits 0 and 1.')
    return (2 * rho01.real, -2 * rho01.imag, diagonal[0] - diagonal[1])
