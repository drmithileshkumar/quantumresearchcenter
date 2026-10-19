#!/usr/bin/env python3
"""Check the Chapter 1–2 worked circuits; uses only the standard library.

Register indices run from the most significant bit at the left (index zero).
These checks verify the mathematics, not the HTML or SVG rendering.
"""
from math import sqrt


def basis(n, index):
    return [complex(i == index) for i in range(2**n)]


def xor_gate(state, n, controls, target):
    out = [0j] * len(state)
    mask = 1 << (n - 1 - target)
    for i, amplitude in enumerate(state):
        j = i ^ mask if all(i & (1 << (n - 1 - c)) for c in controls) else i
        out[j] += amplitude
    return out


def hadamard(state, n, target):
    out = [0j] * len(state)
    mask = 1 << (n - 1 - target)
    for i, amplitude in enumerate(state):
        out[i & ~mask] += amplitude / sqrt(2)
        out[i | mask] += (-1 if i & mask else 1) * amplitude / sqrt(2)
    return out


def equal(actual, expected):
    assert max(abs(a-b) for a, b in zip(actual, expected)) < 1e-12


def main():
    for f0, f1 in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        state = hadamard(hadamard(basis(2, 1), 2, 0), 2, 1)
        queried = [0j] * 4
        for i, amplitude in enumerate(state):
            queried[i ^ (f0 if i // 2 == 0 else f1)] += amplitude
        actual = hadamard(queried, 2, 0)
        expected = [0j] * 4
        expected[2*(f0 ^ f1)] = (-1)**f0 / sqrt(2)
        expected[2*(f0 ^ f1)+1] = -(-1)**f0 / sqrt(2)
        equal(actual, expected)

    compute = [([0, 1], 3), ([3], 4), ([2], 4)]
    gates = compute + [([4], 5)] + compute[::-1]
    for x in range(8):
        a, b, c = (x >> 2) & 1, (x >> 1) & 1, x & 1
        f = (a & b) ^ c
        for y in range(2):
            state = basis(6, 8*x+y)
            for controls, target in gates:
                state = xor_gate(state, 6, controls, target)
            equal(state, basis(6, 8*x+(y ^ f)))
        # A minus target produces the exact phase and restores both scratch bits.
        state = [complex(0)] * 64
        state[8*x], state[8*x+1] = 1/sqrt(2), -1/sqrt(2)
        expected = [(-1)**f * z for z in state]
        for controls, target in gates:
            state = xor_gate(state, 6, controls, target)
        equal(state, expected)

    for x in range(4):
        state = xor_gate(basis(2, x), 2, [1], 0)
        state = xor_gate(state, 2, [], 1)
        equal(state, basis(2, (x+1) % 4))

    # Final exercise: retaining garbage changes the interference readout.
    state = [0j] * 64
    state[0], state[1], state[48], state[49] = [1/sqrt(4), -1/sqrt(4)] * 2
    for controls, target in compute + [([4], 5)]:
        state = xor_gate(state, 6, controls, target)
    dirty = hadamard(xor_gate(state, 6, [0], 1), 6, 0)
    for controls, target in compute[::-1]:
        state = xor_gate(state, 6, controls, target)
    clean = hadamard(xor_gate(state, 6, [0], 1), 6, 0)
    assert abs(sum(abs(z)**2 for z in dirty[32:]) - .5) < 1e-12
    assert abs(sum(abs(z)**2 for z in clean[32:]) - 1) < 1e-12
    print('Verified: all Deutsch functions, clean predicate contracts and phases, incrementer, and garbage interference example.')


if __name__ == '__main__':
    main()
