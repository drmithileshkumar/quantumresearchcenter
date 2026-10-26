#!/usr/bin/env python3
"""Reproducible QKD teaching calculations, not cryptographic software.

The simulator implements a specified individual attack, not arbitrary quantum
attacks. The sampling bound concerns a classical error population. No secret key
is output: certification of a quantum conditional-entropy bound is out of scope.
"""
import argparse
import json
import math
import random


def binary_entropy(q):
    if not 0 <= q <= 1:
        raise ValueError('Probability must lie in [0, 1]')
    return 0.0 if q in (0, 1) else -q * math.log2(q) - (1-q) * math.log2(1-q)


def hypergeom_cdf(population, errors, sample, observed):
    """Exact integer combinatorics followed by float conversion, small blocks."""
    if not 0 <= errors <= population or not 0 <= sample <= population:
        raise ValueError('Invalid population or sample')
    low = max(0, sample - (population-errors))
    high = min(observed, sample, errors)
    numerator = sum(math.comb(errors, k) * math.comb(population-errors, sample-k)
                    for k in range(low, high+1))
    return numerator / math.comb(population, sample)


def population_upper(population, sample, observed, epsilon=0.05):
    """Invert the lower hypergeometric tail; intended for small exact examples."""
    if not 0 <= observed <= sample <= population or sample == population:
        raise ValueError('Require 0 <= observed <= sample < population')
    if not 0 < epsilon < 1:
        raise ValueError('epsilon must lie strictly between zero and one')
    # CDF decreases monotonically with the hypothetical total error count.
    low, high = observed, population - sample + observed
    while low < high:
        mid = (low + high + 1) // 2
        if hypergeom_cdf(population, mid, sample, observed) > epsilon:
            low = mid
        else:
            high = mid - 1
    return low


def random_sample_bound(population, sample, observed, epsilon):
    """Conservative finite-population Hoeffding bound on unseen bit errors.

    Sampling without replacement from a fixed binary population obeys the
    Hoeffding lower-tail bound. Convert a population-mean upper bound into a
    remainder-mean bound. This is NOT a quantum phase-error estimator.
    """
    if not 0 <= observed <= sample < population or sample == 0:
        raise ValueError('Require a nonempty proper sample')
    if not 0 < epsilon < 1:
        raise ValueError('epsilon must lie strictly between zero and one')
    qhat = observed / sample
    delta = math.sqrt(math.log(1/epsilon)/(2*sample))
    return min(1.0, qhat + population/(population-sample)*delta)


def simulate(signals=20000, attack=0.2, seed=7, test_fraction=0.2):
    if signals < 10 or not 0 <= attack <= 1 or not 0 < test_fraction < 1:
        raise ValueError('Need >=10 signals, attack in [0,1], and test fraction in (0,1)')
    rng = random.Random(seed)
    sifted = []
    for _ in range(signals):
        bit, basis, bob_basis = (rng.randrange(2) for _ in range(3))
        transmitted_bit, transmitted_basis = bit, basis
        if rng.random() < attack:
            eve_basis = rng.randrange(2)
            eve_bit = bit if eve_basis == basis else rng.randrange(2)
            transmitted_bit, transmitted_basis = eve_bit, eve_basis
        bob_bit = transmitted_bit if bob_basis == transmitted_basis else rng.randrange(2)
        if basis == bob_basis:
            sifted.append((bit, bob_bit))
    if len(sifted) < 2:
        raise ValueError('Insufficient sifted rounds; increase signals')
    # Random permutation is independent of outcomes; then take a fixed-size prefix.
    rng.shuffle(sifted)
    m = max(1, min(len(sifted)-1, int(len(sifted)*test_fraction)))
    test, raw = sifted[:m], sifted[m:]
    test_errors = sum(a != b for a, b in test)
    raw_errors = sum(a != b for a, b in raw)
    epsilon = 1e-6
    return dict(seed=seed, emitted=signals, detected=signals, sifted=len(sifted),
                tested=m, raw_unrevealed=len(raw), test_errors=test_errors,
                test_qber=test_errors/m, expected_qber=attack/4,
                raw_qber_simulator_only=raw_errors/len(raw),
                classical_unseen_error_upper=random_sample_bound(len(sifted), m, test_errors, epsilon),
                sampling_failure=epsilon, secret_key=None,
                scope='Ideal intercept-resend simulation; classical sampling only; no entropy certification.')


HAMMING_CHECK = ((0,0,0,1,1,1,1), (0,1,1,0,0,1,1), (1,0,1,0,1,0,1))


def matvec(matrix, bits):
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError('Expected binary bits')
    if any(len(row) != len(bits) or any(x not in (0, 1) for x in row) for row in matrix):
        raise ValueError('Expected a compatible binary matrix')
    return [sum(a*b for a, b in zip(row, bits)) % 2 for row in matrix]


def reconcile_one_error(alice, bob):
    if len(alice) != 7 or len(bob) != 7:
        raise ValueError('This teaching decoder requires seven-bit blocks')
    sa, sb = matvec(HAMMING_CHECK, alice), matvec(HAMMING_CHECK, bob)
    difference = [a ^ b for a, b in zip(sa, sb)]
    position = sum(bit << (2-i) for i, bit in enumerate(difference))
    corrected = list(bob)
    if position:
        corrected[position-1] ^= 1
    return corrected, sa, difference


def toeplitz(seed, bits, length):
    """T[i,j] = seed[n-1+i-j], with fresh uniform seed for theorem use."""
    n = len(bits)
    if n < 1 or length < 1 or len(seed) != n+length-1:
        raise ValueError('Toeplitz seed length must be input length + output length - 1')
    return matvec([[seed[n-1+i-j] for j in range(n)] for i in range(length)], bits)


def key_budget(entropy, leakage, verification, pa_exponent, authentication):
    """Assumes a certified pre-transcript *unsmoothed* min-entropy lower bound.

    If a smooth bound is supplied, its error contribution needs separate handling.
    pa_exponent=s means epsilon_PA=2**(-s). Negative net expansion is not growth.
    """
    values = (entropy, leakage, verification, pa_exponent, authentication)
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('Budgets must be finite and nonnegative')
    length = math.floor(entropy - leakage - verification - 2*pa_exponent)
    if length <= 0:
        return dict(abort=True, output_bits=0, net_expansion_bits=0)
    return dict(abort=False, output_bits=length, net_expansion_bits=length-authentication)


def decoy_lower(mu, nu, q_mu, q_nu, vacuum):
    """Asymptotic vacuum+weak decoy bound; no finite-count uncertainty included."""
    if not 0 < nu < mu or any(not 0 <= q <= 1 for q in (q_mu, q_nu, vacuum)):
        raise ValueError('Need 0 < nu < mu and valid gains')
    value = mu/(mu*nu-nu*nu) * (q_nu*math.exp(nu) - (nu/mu)**2*q_mu*math.exp(mu)
                               - (1-(nu/mu)**2)*vacuum)
    if value > 1 + 1e-12:
        raise ValueError('Inconsistent exact gains imply an unphysical yield bound')
    return max(0.0, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--signals', type=int, default=20000)
    parser.add_argument('--attack', type=float, default=0.2)
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--test-fraction', type=float, default=0.2)
    args = parser.parse_args()
    try:
        result = simulate(args.signals, args.attack, args.seed, args.test_fraction)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))
    print('Exact small-block example:', population_upper(20, 5, 0, 0.05), 'total errors allowed')
    print('Assumed-entropy budget:', key_budget(7500, 1300, 40, 40, 128))


if __name__ == '__main__':
    main()
