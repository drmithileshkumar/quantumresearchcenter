#!/usr/bin/env python3
"""Reproduce course calculations independently of the HTML build. Requires NumPy."""
import math
import numpy as np


def entropy(rho):
    values = np.linalg.eigvalsh(rho)
    assert values.min() >= -1e-12
    return -sum(float(x) * math.log2(float(x)) for x in values if x > 1e-14)


def trace_distance(a, b):
    return np.linalg.norm(a - b, ord='nuc') / 2


def main():
    zero = np.array([1., 0.]); plus = np.array([1., 1.]) / np.sqrt(2)
    rho = np.outer(zero, zero); sigma = np.outer(plus, plus)
    assert np.isclose((1 + trace_distance(rho, sigma)) / 2, 0.8535533905932737)
    # Build the actual optimal measurement and compare with the norm formula.
    for theta in np.linspace(0, np.pi / 2, 25):
        psi = np.array([np.cos(theta), np.sin(theta)])
        other = np.outer(psi, psi)
        for prior in (0.2, 0.5, 0.8):
            diff = prior * rho - (1 - prior) * other
            values, vectors = np.linalg.eigh(diff)
            effect = vectors[:, values > 1e-12] @ vectors[:, values > 1e-12].T
            success = prior * np.trace(effect @ rho) + (1-prior) * np.trace((np.eye(2)-effect) @ other)
            bound = (1 + np.linalg.norm(diff, ord='nuc')) / 2
            assert np.isclose(success, bound)
    # Dilation / Kraus and Choi checks, including a reference system.
    gamma = 0.36
    kraus = [np.diag([1., np.sqrt(1-gamma)]), np.array([[0., np.sqrt(gamma)], [0., 0.]])]
    assert np.allclose(sum(k.T @ k for k in kraus), np.eye(2))
    damped = sum(k @ sigma @ k.T for k in kraus)
    assert np.allclose(damped, [[0.68, 0.4], [0.4, 0.32]])
    omega = np.array([1., 0., 0., 1.])
    choi = sum(np.outer(np.kron(np.eye(2), k) @ omega, np.kron(np.eye(2), k) @ omega) for k in kraus)
    assert np.linalg.eigvalsh(choi).min() >= -1e-12
    assert np.allclose(np.trace(choi.reshape(2,2,2,2), axis1=1, axis2=3), np.eye(2))
    bell = np.outer(omega, omega) / 2
    pt = bell.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
    assert np.allclose(np.linalg.eigvalsh(pt), [-0.5, 0.5, 0.5, 0.5])
    assert np.isclose(entropy(np.diag([0.8, 0.2])), 0.7219280948873623)
    assert np.isclose(entropy((rho + sigma) / 2), 0.6008760366928562)
    # Both LOCC branches must reach the same target after the correction.
    target = np.array([np.sqrt(0.8), 0., 0., np.sqrt(0.2)])
    x = np.array([[0.,1.],[1.,0.]])
    for a, correction in [(np.diag(np.sqrt([0.8,0.2])), np.eye(4)), (np.diag(np.sqrt([0.2,0.8])), np.kron(x,x))]:
        branch = np.kron(a,np.eye(2)) @ (omega/np.sqrt(2))
        assert np.isclose(branch @ branch, 0.5)
        assert np.allclose(correction @ branch / np.linalg.norm(branch), target)
    mass = sum(math.comb(10,k)*0.2**k*0.8**(10-k) for k in range(4))
    assert sum(math.comb(10,k) for k in range(4)) == 176
    assert np.isclose(mass, 0.8791261184)
    print(f'Compression n=10, k=3: mass={mass:.9f}, fidelity lower bound={mass**2:.9f}')
    # Check the code condition as matrices, then exhibit its phase-error failure.
    code = np.eye(8)[:, [0,7]]
    errors = [np.eye(8)] + [np.kron(np.kron(x if i==0 else np.eye(2), x if i==1 else np.eye(2)), x if i==2 else np.eye(2)) for i in range(3)]
    for i,a in enumerate(errors):
        for j,b in enumerate(errors):
            assert np.allclose(code.T @ a.T @ b @ code, np.eye(2) if i==j else np.zeros((2,2)))
    z1 = np.kron(np.diag([1.,-1.]), np.eye(4))
    assert np.allclose(code.T @ z1 @ code, np.diag([1.,-1.]))
    for p in (0.01,0.1,0.3):
        enumerated = sum(math.comb(3,k)*p**k*(1-p)**(3-k) for k in (2,3))
        assert np.isclose(enumerated, 3*p*p-2*p**3)
    assert np.isclose(3*0.01*0.99**2+0.01**3, 0.029404)
    assert np.isclose(2**(-0.1), 0.9330329915368074)
    print('PASS: discrimination, Kraus/Choi consistency, entropy, LOCC branches, compression, and code correction examples.')


if __name__ == '__main__':
    main()
