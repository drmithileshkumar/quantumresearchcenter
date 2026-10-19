#!/usr/bin/env python3
"""Numerically check the small worked examples in Chapters 3–11 (requires NumPy).

Each check reproduces a number or identity stated in a manuscript. Register
order is most significant qubit first. These checks confirm examples, not the
general theorems the text cites.
"""
from fractions import Fraction
from math import asin, comb, cos, gcd, pi, sin, sqrt
import numpy as np

X = np.array([[0, 1], [1, 0]], complex); Z = np.diag([1, -1]).astype(complex)
Y = np.array([[0, -1j], [1j, 0]]); I2 = np.eye(2); Hd = np.array([[1, 1], [1, -1]]) / sqrt(2)
P = lambda t: np.diag([1, np.exp(1j * t)])
def kron(*ms):
    out = np.eye(1)
    for m in ms: out = np.kron(out, m)
    return out
def expm_h(H, t):
    w, v = np.linalg.eigh(H); return v @ np.diag(np.exp(-1j * w * t)) @ v.conj().T
def close(a, b, tol=1e-9): assert np.allclose(a, b, atol=tol), (a, b)
def fourier(N): return np.array([[np.exp(2j * pi * x * y / N) for x in range(N)] for y in range(N)]) / sqrt(N)

def chapter3():
    n, s = 3, 0b101  # Bernstein–Vazirani: signs then Hadamards give |s>
    Hn = kron(*[Hd] * n); signs = np.array([(-1) ** bin(s & x).count('1') for x in range(8)]) / sqrt(8)
    close(Hn @ signs, np.eye(8)[s])
    assert [(5 - 3) / 8][0] ** 2 == 1 / 16  # Deutsch–Jozsa outside the promise
    s = 0b110; allowed = {z for z in range(8) if bin(s & z).count('1') % 2 == 0}  # Simon
    assert allowed == {0b000, 0b001, 0b110, 0b111}
    assert abs(7 * 6 * 4 / 512 - 0.328125) < 1e-12
    chi = np.array([np.exp(-2j * pi * y / 4) for y in range(4)]) / 2  # phase-gradient state
    close(np.roll(chi, 1), 1j * chi)
    close(np.exp(1j * pi) * np.exp(1j * pi / 4), np.exp(2j * pi * 5 / 8))  # Z, S, T phases for v=5

def chapter4():
    F8 = fourier(8)
    close(F8 @ (np.eye(8)[[0, 2, 4, 6]].sum(0) / 2), (np.eye(8)[0] + np.eye(8)[4]) / sqrt(2))
    close(F8 @ (np.eye(8)[[1, 3, 5, 7]].sum(0) / 2), (np.eye(8)[0] - np.eye(8)[4]) / sqrt(2))
    swap = np.eye(4)[[0, 2, 1, 3]]; cp = np.diag([1, 1, 1, 1j])  # two-qubit QFT circuit
    close(swap @ kron(I2, Hd) @ cp @ kron(Hd, I2), fourier(4))
    probs = [abs(sum(np.exp(2j * pi * k * (0.3 - j / 8)) for k in range(8)) / 8) ** 2 for j in range(8)]
    assert abs(probs[2] - 0.5775) < 1e-3 and abs(probs[3] - 0.2593) < 1e-3
    assert min(abs(sum(np.exp(2j * pi * k * (phi - round(phi * 8) / 8)) for k in range(8)) / 8) ** 2
               for phi in np.linspace(0, 1, 401)) >= 4 / pi ** 2 - 1e-9
    orbit = [pow(7, k, 15) for k in range(4)]; assert orbit == [1, 7, 4, 13]
    U = np.zeros((16, 16))
    for y in range(16): U[(7 * y) % 15 if y < 15 else y, y] = 1
    u1 = sum(np.exp(-2j * pi * k / 4) * np.eye(16)[orbit[k]] for k in range(4)) / 2
    close(U @ u1, 1j * u1)
    assert Fraction(85, 512).limit_denominator(20) == Fraction(1, 6) and pow(2, 6, 21) == 1
    assert (gcd(7 ** 2 - 1, 15), gcd(7 ** 2 + 1, 15)) == (3, 5)
    assert (gcd(2 ** 3 - 1, 21), gcd(2 ** 3 + 1, 21)) == (7, 3)
    assert (gcd(2 ** 6 - 1, 35), gcd(2 ** 6 + 1, 35)) == (7, 5) and pow(2, 12, 35) == 1
    assert [pow(5, k, 33) for k in range(1, 11)][-1] == 1 and pow(5, 5, 33) == 23

def chapter5():
    t = asin(1 / 3); assert abs(sin(3 * t) ** 2 - 0.7257) < 1e-3 and abs(sin(5 * t) ** 2 - 0.9836) < 1e-3
    t = asin(0.1); assert round(pi / (4 * t) - 0.5) == 7 and abs(sin(15 * t) ** 2 - 0.9953) < 1e-3
    assert abs(sin(29 * t) ** 2 - 0.055) < 2e-3
    for eps in (0.5, 0.3, 0.1):  # pi/3 fixed point gives failure eps^3
        th = asin(sqrt(1 - eps)); A = np.array([[cos(th), -sin(th)], [sin(th), cos(th)]])
        w = np.exp(1j * pi / 3); R0 = np.diag([w, 1]); RG = np.diag([1, w])
        assert abs(abs((A @ R0 @ A.conj().T @ RG @ A)[0, 0]) ** 2 - eps ** 3) < 1e-12
    th = 0.4; Q = np.array([[cos(2 * th), sin(2 * th)], [-sin(2 * th), cos(2 * th)]])
    vp = np.array([1, 1j]) / sqrt(2); close(Q @ vp, np.exp(2j * th) * vp)
    psi = -1j * np.exp(1j * th) / sqrt(2) * vp + 1j * np.exp(-1j * th) / sqrt(2) * np.array([1, -1j]) / sqrt(2)
    close(psi, [sin(th), cos(th)])
    assert abs(sin(11 * pi / 64) ** 2 - 0.2643) < 1e-3

def chapter6():
    psi = np.zeros((2, 4), complex); psi[0, 0] = 1
    for _ in range(3):
        psi = Hd @ psi; psi = np.array([np.roll(psi[0], -1), np.roll(psi[1], 1)])
    close(psi, np.array([[0, 0, 0, 1], [0, 0, 0, 1]]) / sqrt(2))
    T = 60; psi = np.zeros((2, 2 * T + 1), complex); psi[:, T] = [1 / sqrt(2), 1j / sqrt(2)]
    for _ in range(T):
        psi = Hd @ psi; new = np.zeros_like(psi); new[0, :-1] = psi[0, 1:]; new[1, 1:] = psi[1, :-1]; psi = new
    p = (abs(psi) ** 2).sum(0); x = np.arange(-T, T + 1); assert abs(sqrt((p * x * x).sum()) - 32.5) < 0.1
    A = np.roll(np.eye(4), 1, 0) + np.roll(np.eye(4), -1, 0)
    for t in (0.3, 1.1): assert abs(expm_h(A, t)[2, 0] - (-sin(t) ** 2)) < 1e-12
    assert abs(2 * np.arccos(0.5) - 2 * pi / 3) < 1e-12

def chapter7():
    A = np.diag([1, .5]); B = np.diag([0, sqrt(3) / 2]); U = np.block([[A, B], [B, -A]])
    close(U @ U, np.eye(4)); out = U @ np.r_[np.ones(2) / sqrt(2), 0, 0]
    assert abs(np.linalg.norm(out[:2]) ** 2 - 5 / 8) < 1e-12
    W = kron(Hd, I2) @ np.block([[I2, 0 * I2], [0 * I2, X]]) @ kron(Hd, I2)
    close(W[:2, :2], (I2 + X) / 2)
    Hm = 0.5 * kron(Z, Z) - 0.3 * kron(X, I2); a = np.sqrt([0.5 / 0.8, 0.3 / 0.8])
    Pr = np.array([[a[0], -a[1]], [a[1], a[0]]])
    SEL = np.block([[kron(Z, Z), np.zeros((4, 4))], [np.zeros((4, 4)), -kron(X, I2)]])
    Ub = kron(Pr.T, np.eye(4)) @ SEL @ kron(Pr, np.eye(4)); close(Ub[:4, :4], Hm / 0.8)
    assert abs(np.linalg.norm(np.linalg.eigvalsh(kron(X, X) + kron(Y, Y) + kron(Z, Z)), np.inf) - 3) < 1e-12
    Hv = 2 * kron(Z, I2) + kron(Z, Z) - 0.5 * kron(I2, X); v = Hv @ np.eye(4)[0]
    assert abs(np.linalg.norm(v) ** 2 / 3.5 ** 2 - 0.755) < 1e-3

def chapter8():
    def Wx(x): s = sqrt(1 - x * x); return np.array([[x, 1j * s], [1j * s, x]])
    for x in (0, 0.3, 0.8):
        assert abs(np.linalg.matrix_power(Wx(x), 3)[0, 0] - (4 * x ** 3 - 3 * x)) < 1e-12
        for phi in (0, pi / 4, pi / 2):
            val = (Wx(x) @ np.diag([np.exp(1j * phi), np.exp(-1j * phi)]) @ Wx(x))[0, 0]
            assert abs(val - (cos(phi) * (2 * x * x - 1) + 1j * sin(phi))) < 1e-12
    Hm = 0.5 * kron(Z, Z) - 0.3 * kron(X, I2); a = np.sqrt([0.5 / 0.8, 0.3 / 0.8])
    Pr = np.array([[a[0], -a[1]], [a[1], a[0]]])
    SEL = np.block([[kron(Z, Z), np.zeros((4, 4))], [np.zeros((4, 4)), -kron(X, I2)]])
    Ub = kron(Pr.T, np.eye(4)) @ SEL @ kron(Pr, np.eye(4)); close(Ub, Ub.conj().T)
    phases = sorted(abs(np.angle(np.linalg.eigvals(kron(2 * np.outer([1, 0], [1, 0]) - I2, np.eye(4)) @ Ub))))
    expected = sorted(list(np.arccos(np.linalg.eigvalsh(Hm) / 0.8)) * 2)
    close(phases, expected, 1e-8)
    assert abs(np.linalg.norm(np.diag([1, 10]) @ np.ones(2) / sqrt(2) / 10) ** 2 - 0.505) < 1e-12

def chapter9():
    E = expm_h(X + Z, 1)
    close(expm_h(X + Z, pi / (2 * sqrt(2))), -1j * Hd)
    err = lambda r: np.linalg.norm(E - np.linalg.matrix_power(expm_h(X, 1 / r) @ expm_h(Z, 1 / r), r), 2)
    err2 = lambda r: np.linalg.norm(E - np.linalg.matrix_power(expm_h(X, .5 / r) @ expm_h(Z, 1 / r) @ expm_h(X, .5 / r), r), 2)
    assert err(100) < 0.01 and 0.006 < err(100) < 0.008 and abs(err(10) - 0.07) < 0.002 and abs(err2(10) - 0.0027) < 2e-4
    close(X @ Z - Z @ X, -2j * Y)
    zz = expm_h(kron(Z, Z), 0.37); cn = np.eye(4)[[0, 1, 3, 2]]
    close(cn @ kron(I2, np.diag([np.exp(-0.37j), np.exp(0.37j)])) @ cn, zz)
    def run(T, steps=3000):
        psi = np.array([1, 1], complex) / sqrt(2); dt = T / steps
        for k in range(steps):
            s = (k + .5) / steps; psi = expm_h(-(1 - s) * X - s * Z, dt) @ psi
        return abs(psi[0]) ** 2
    assert abs(run(4) - 0.986) < 2e-3 and run(8) > 0.999

def chapter10():
    def state(t):
        return cos(t / 2) * np.eye(4)[0] + sin(t / 2) * np.eye(4)[3]
    H = -kron(Z, Z) - kron(X, X); E = lambda t: np.real(state(t) @ H @ state(t))
    for t in (0, pi / 3, 1.0, pi / 2): assert abs(E(t) - (-1 - sin(t))) < 1e-12
    assert abs((E(pi / 3 + pi / 2) - E(pi / 3 - pi / 2)) / 2 + cos(pi / 3)) < 1e-12
    C = (np.eye(4) - kron(Z, Z)) / 2; B = kron(X, I2) + kron(I2, X)
    F = lambda g, b: np.real((s := expm_h(B, b) @ expm_h(C, g) @ (np.ones(4) / 2)).conj() @ C @ s)
    for g, b in ((pi / 2, pi / 8), (1, 0.3), (pi / 2, 3 * pi / 8)):
        assert abs(F(g, b) - (0.5 + 0.5 * sin(4 * b) * sin(g))) < 1e-12

def chapter11():
    rng = np.random.default_rng(7); v = rng.normal(size=2) + 1j * rng.normal(size=2); psi = v / np.linalg.norm(v)
    st = np.diag([1, 1, 1, -1]) @ np.kron(psi, np.ones(2) / sqrt(2))
    for al in (0, 0.7):
        for m in (0, 1):
            out = np.kron(np.array([1, (-1) ** m * np.exp(1j * al)]).conj() / sqrt(2), I2) @ st
            pred = np.linalg.matrix_power(X, m) @ Hd @ P(-al) @ psi / sqrt(2)
            assert abs(abs(out.conj() @ pred) - 0.5) < 1e-12
    w = np.exp(1j * pi / 4); st = np.eye(4)[[0, 1, 3, 2]] @ np.kron(psi, np.array([1, w]) / sqrt(2))
    for m in (0, 1):
        out = st.reshape(2, 2)[:, m]; out = out / np.linalg.norm(out)
        if m: out = np.diag([1, 1j]) @ out
        assert abs(abs(out.conj() @ (np.diag([1, w]) @ psi)) - 1) < 1e-12
    th = 0.9; U = expm_h(-X, th); R = expm_h(-X, th / 2)
    close((I2 + U) / 2, cos(th / 2) * R); close((I2 - U) / 2, -1j * sin(th / 2) * R @ X)
    for num, bits in ((3, (0, 1, 1)), (5, (1, 0, 1)), (7, (1, 1, 1))):
        phi, m, found = num / 8, 3, {}
        for k in range(m, 0, -1):
            omega = 2 * pi * sum(found[j] * 2 ** (k - 1 - j) for j in range(k + 1, m + 1))
            phase = 2 * pi * 2 ** (k - 1) * phi - omega
            p0 = abs((1 + np.exp(1j * phase)) / 2) ** 2; assert p0 < 1e-12 or p0 > 1 - 1e-12
            found[k] = 0 if p0 > 0.5 else 1
        assert tuple(found[j] for j in (1, 2, 3)) == bits
    assert abs(35 * (35e-9) ** 3 - 1.5e-21) < 1e-22

if __name__ == '__main__':
    for check in (chapter3, chapter4, chapter5, chapter6, chapter7, chapter8, chapter9, chapter10, chapter11): check()
    print('Verified Chapter 3–11 worked examples: phase encoding, Fourier and factoring, amplification, walks, '
          'block encodings, signal processing, product formulas, adiabatic and variational examples, adaptive measurement.')
