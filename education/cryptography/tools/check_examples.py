#!/usr/bin/env python3
"""Reproduce classroom calculations; this is not a QKD security proof."""
from math import exp, log, log2, sqrt, isclose
from itertools import product
from pathlib import Path
import sys
from math import sin, cos, pi, comb
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from bb84_lab import (binary_entropy, hypergeom_cdf, population_upper, simulate,
                      matvec, reconcile_one_error, toeplitz, key_budget, decoy_lower)


def entropy(q):
    return 0.0 if q in (0, 1) else -q * log2(q) - (1-q) * log2(1-q)


def main():
    # Enumerate Eve's basis choice and the unbiased result on a mismatch.
    errors = sum(eve_wrong and outcome_wrong
                 for eve_wrong, outcome_wrong in product((0, 1), repeat=2)) / 4
    assert errors == 0.25
    assert isclose(0.2 * errors, 0.05)
    assert isclose(0.75**10, 0.0563135147, abs_tol=1e-10)
    assert isclose(0.02 + sqrt(log(1e6)/20000), 0.0462826, abs_tol=1e-7)
    assert isclose(1-2*entropy(0.05), 0.427206, abs_tol=1e-6)
    assert sum(sum(bits) % 2 == 0 for bits in product((0, 1), repeat=4)) == 8
    assert 600 - 2*log2(2**40) == 520
    assert 8000 - 1200 - 80 - 128 == 6592
    assert isclose(1-exp(-0.1)*1.1, 0.00467884, abs_tol=1e-8)
    assert isclose(0.1*exp(-0.1), 0.09048374, abs_tol=1e-8)
    assert isclose(1e6 * 10**(-0.2*50/10) * 0.2 / 2, 10000)
    # Pauli conjugation cancels each Bloch coordinate over four uniform keys.
    signs = ((1,1,1), (1,-1,-1), (-1,1,-1), (-1,-1,1))
    assert all(sum(row[j] for row in signs) == 0 for j in range(3))
    # Every one-bit corruption of every seven-bit string is corrected.
    for word in product((0, 1), repeat=7):
        for position in range(7):
            received = list(word)
            received[position] ^= 1
            corrected, _, _ = reconcile_one_error(word, received)
            assert corrected == list(word)
    original = [1,0,1,1,0,0,1]
    corrupt = list(original)
    corrupt[0] ^= 1
    corrupt[1] ^= 1
    assert reconcile_one_error(original, corrupt)[0] != original
    assert matvec(((1,0,1,1), (0,1,0,1)), [1,0,1,1]) == [1,1]
    # Verify the universal collision bound for ALL nonzero differences.
    for difference in list(product((0,1), repeat=4))[1:]:
        collisions = sum(toeplitz(seed, difference, 2) == [0,0]
                         for seed in product((0,1), repeat=5))
        assert collisions == 8
    # Exact sampling inversion: check coverage against every population in
    # small exhaustive instances, not just the example used in the manuscript.
    assert population_upper(20, 5, 0, 0.05) == 8
    assert isclose(hypergeom_cdf(20,10,5,0), 252/15504)
    for n in range(2, 15):
        for m in range(1, n):
            for errors in range(n+1):
                failure = 0.0
                for t in range(max(0,m-(n-errors)), min(m,errors)+1):
                    if population_upper(n,m,t,0.05) < errors:
                        failure += comb(errors,t)*comb(n-errors,m-t)/comb(n,m)
                assert failure <= 0.05 + 1e-12
    # Four real-state projectors, independently summing Born probabilities
    # for Eve's branches and Bob's wrong outcome.
    for theta in (0, pi/12, pi/8, pi/4):
        eve = ((cos(theta),sin(theta)),(-sin(theta),cos(theta)))
        inner = lambda a,b: sum(x*y for x,y in zip(a,b))
        z0,z1=(1,0),(0,1)
        plus,minus=(1/sqrt(2),1/sqrt(2)),(1/sqrt(2),-1/sqrt(2))
        qz=sum(inner(z0,e)**2*inner(z1,e)**2 for e in eve)
        qx=sum(inner(plus,e)**2*inner(minus,e)**2 for e in eve)
        assert isclose(qz,0.5*sin(2*theta)**2,abs_tol=1e-12)
        assert isclose(qx,0.5*cos(2*theta)**2,abs_tol=1e-12)
        assert isclose((qz+qx)/2,0.25,abs_tol=1e-12)
    assert key_budget(7500,1300,40,40,128) == dict(abort=False,output_bits=6080,net_expansion_bits=5952)
    assert key_budget(70,0,0,40,0)['abort']
    assert key_budget(6000,0,40,40,0)['output_bits'] == 5880
    for eta in (0.001,0.01,0.1,0.9):
        lower = decoy_lower(.5,.1,1-exp(-eta*.5),1-exp(-eta*.1),0)
        assert 0 <= lower <= eta + 1e-12
    yield_lower=decoy_lower(.5,.1,1-exp(-.05),1-exp(-.01),0)
    assert isclose(yield_lower,0.0972533870,abs_tol=1e-10)
    assert isclose(1-2.15*binary_entropy(.05),0.3842465422,abs_tol=1e-10)
    assert isclose(1-binary_entropy(.06)-binary_entropy(.08),0.270376,abs_tol=1e-6)
    assert isclose((1-exp(-.1)*1.1)/(1-exp(-.1)),0.0491668,abs_tol=1e-7)
    for attack in (0,.2,1):
        result=simulate(100000,attack,7)
        assert result['sifted'] == result['tested']+result['raw_unrevealed']
        assert result['secret_key'] is None
        assert abs(result['test_qber']-attack/4) < .02
        if attack == 0:
            assert result['test_errors'] == result['raw_qber_simulator_only'] == 0
    assert simulate(100,0.2,3) == simulate(100,0.2,3)
    print('PASS: 896 single-error corrections, every 2x4 Toeplitz collision, exhaustive small sampling coverage, Born-rule attacks, extraction budgets, decoy bounds, and seeded simulations.')


if __name__ == '__main__':
    main()
