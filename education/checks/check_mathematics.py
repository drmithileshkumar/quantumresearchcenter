#!/usr/bin/env python3
"""Verify worked small instances in Algorithms and Information (NumPy only).

These checks are independent of the HTML renderer. They check finite examples,
not the general coding, complexity, or security theorems cited in the lessons.
"""
import numpy as np
from math import sqrt, pi

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
H = (X + Z) / sqrt(2)
zero, one = I[:, 0], I[:, 1]
plus, minus = H[:, 0], H[:, 1]


def same(a, b):
    assert np.allclose(a, b, atol=1e-12, rtol=1e-12), (a, b)


def outer(v):
    return np.outer(v, v.conj())


def entropy(rho):
    values = np.linalg.eigvalsh(rho)
    return -sum(x*np.log2(x) for x in values if x > 1e-14)


def evolution(a, t):
    vals, vecs = np.linalg.eigh(a)
    return (vecs * np.exp(-1j*t*vals)) @ vecs.conj().T


def fourier(n):
    return np.exp(2j*pi*np.outer(np.arange(n), np.arange(n))/n)/sqrt(n)


def algorithms():
    # Arbitrary-length hidden string example, including all secrets through n=5.
    for n in range(1, 6):
        size = 2**n
        had = np.array([[(-1)**((x & y).bit_count())/sqrt(size)
                         for x in range(size)] for y in range(size)])
        for secret in range(size):
            phase = np.array([(-1)**((secret & x).bit_count())/sqrt(size)
                              for x in range(size)])
            same(had @ phase, np.eye(size)[:, secret])
    even = np.array([1, 0, 1, 0, 1, 0, 1, 0])/2
    target = np.zeros(8); target[[0, 4]] = 1/sqrt(2)
    same(fourier(8) @ even, target)
    target[4] *= -1
    same(fourier(8) @ np.roll(even, 1), target)
    phase = np.exp(2j*pi*np.arange(8)*3/8)/sqrt(8)
    same(fourier(8).conj().T @ phase, np.eye(8)[:, 3])
    for p in (.1, .25, .5, .8):
        psi = np.array([sqrt(p), sqrt(1-p)])
        reflection = 2*outer(psi)-I
        Q = reflection @ np.diag([-1, 1])
        theta = np.arcsin(sqrt(p))
        same(Q @ psi, [np.sin(3*theta), np.cos(3*theta)])
        A = np.array([[sqrt(p), -sqrt(1-p)], [sqrt(1-p), sqrt(p)]])
        R = np.diag([np.exp(1j*pi/3), 1])
        result = A @ R @ A.T @ R @ A @ zero
        same(abs(result[1])**2, (1-p)**3)
    # Exact amplification by tuning a separate success flag.
    for p in (.001, .1, .25, .5, .8, 1):
        theta=np.arcsin(sqrt(p))
        k=int(np.ceil(pi/(4*theta)-.5))
        tuned=pi/(4*k+2)
        assert np.sin(tuned)**2 <= p+1e-12
        same(np.sin((2*k+1)*tuned)**2,1)
    # Coin-major indexing for the cycle of length four.
    shift = np.zeros((8, 8))
    for c in range(2):
        for x in range(4):
            shift[c*4+(x+(-1 if c==0 else 1))%4, c*4+x] = 1
    walk = shift @ np.kron(H, np.eye(4))
    state2 = walk @ walk @ np.eye(8)[:, 0]
    expected = np.zeros(8); expected[[2,4,0]]=0.5;expected[6]=-.5
    same(state2, expected)
    same((walk@state2)[1], 0)
    same((walk@state2)[7], 1/sqrt(2))
    A=np.diag([1,.5]);B=np.diag([0,sqrt(3)/2]);U=np.block([[A,B],[B,-A]])
    same(U.conj().T@U,np.eye(4));same(np.linalg.norm(A@plus)**2,5/8)
    for x in np.linspace(-1,1,21):
        W=x*I+1j*sqrt(max(0,1-x*x))*X
        same((W@W)[0,0],2*x*x-1)
    for r in (10,20,40):
        approximate=np.linalg.matrix_power(evolution(X,1/r)@evolution(Z,1/r),r)
        assert np.linalg.norm(approximate-evolution(X+Z,1),2) <= 1/r+1e-12
    for theta in (0,.4,pi/2,pi):
        v=np.array([np.cos(theta/2),0,0,np.sin(theta/2)])
        same(np.vdot(v,(-np.kron(Z,Z)-np.kron(X,X))@v),-1-np.sin(theta))
    # One-bit measurement teleportation, including complex inputs and both outcomes.
    psi=np.array([sqrt(.3),1j*sqrt(.7)])
    CZ=np.diag([1,1,1,-1])
    for alpha in (0,.3,1.1):
        joint=CZ@np.kron(psi,plus)
        for m in (0,1):
            bra=np.array([1,(-1)**m*np.exp(-1j*alpha)])/sqrt(2)
            branch=np.kron(bra,I)@joint
            expected=np.linalg.matrix_power(X,m)@H@np.diag([1,np.exp(-1j*alpha)])@psi/sqrt(2)
            same(branch,expected)
    print('Algorithms: phase, Fourier, amplification, walks, blocks, polynomials, evolution, variational and adaptive examples PASS')


def information():
    bell=np.array([1,0,0,1])/sqrt(2)
    rho=outer(bell)
    reduced=np.trace(rho.reshape(2,2,2,2),axis1=1,axis2=3)
    same(reduced,I/2);same(np.kron(H,H)@bell,bell)
    same((outer(plus)+outer(minus))/2,I/2)
    for gamma in (0,.2,1):
        K0=np.diag([1,sqrt(1-gamma)]);K1=np.array([[0,sqrt(gamma)],[0,0]])
        same(K0.conj().T@K0+K1.conj().T@K1,I)
        result=K0@outer(plus)@K0.conj().T+K1@outer(plus)@K1.conj().T
        same(result,[[.5+.5*gamma,.5*sqrt(1-gamma)],[.5*sqrt(1-gamma),.5*(1-gamma)]])
    partial_transpose=rho.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
    same(np.linalg.eigvalsh(partial_transpose),[-.5,.5,.5,.5])
    delta=(outer(zero)-outer(plus))/2
    same(np.linalg.eigvalsh(delta),[-1/(2*sqrt(2)),1/(2*sqrt(2))])
    c=1/(1+1/sqrt(2));E0=c*outer(minus);E1=c*outer(one);Efail=I-E0-E1
    assert min(np.linalg.eigvalsh(Efail)) > -1e-12
    same(np.vdot(plus,E0@plus),0);same(np.vdot(zero,E1@zero),0)
    same(.5*np.vdot(zero,E0@zero)+.5*np.vdot(plus,E1@plus),1-1/sqrt(2))
    same(entropy(rho),0);same(entropy(reduced),1)
    average=(outer(zero)+outer(plus))/2
    assert abs(entropy(average)-.6008760366928562) < 1e-12
    for p in (.5,.75,.9,1):
        state=np.array([sqrt(p),0,0,sqrt(1-p)])
        K=np.diag([sqrt((1-p)/p),1]);result=np.kron(K,I)@state
        same(np.vdot(result,result),2*(1-p))
        if p<1:same(result/np.linalg.norm(result),bell)
    # Error syndromes preserve both logical amplitudes.
    logical=np.zeros(8,dtype=complex);logical[0]=sqrt(.3);logical[7]=1j*sqrt(.7)
    checks=[np.kron(np.kron(Z,Z),I),np.kron(np.kron(I,Z),Z)]
    errors=[np.eye(8),np.kron(np.kron(X,I),I),np.kron(np.kron(I,X),I),np.kron(np.kron(I,I),X)]
    for E,signs in zip(errors,[(1,1),(-1,1),(-1,-1),(1,-1)]):
        corrupted=E@logical
        for P,sign in zip(checks,signs):same(P@corrupted,sign*corrupted)
        same(E@corrupted,logical)
    # Teleportation branch formula for arbitrary complex input, MSB-first ordering.
    psi=np.array([sqrt(.3),1j*sqrt(.7)])
    start=np.kron(psi,bell);cx=np.zeros((8,8))
    for i in range(8):cx[i ^ (2 if i & 4 else 0),i]=1
    state=np.kron(np.kron(H,I),I)@cx@start
    for m in (0,1):
        for n in (0,1):
            branch=state[4*m+2*n:4*m+2*n+2]
            same(branch,np.linalg.matrix_power(X,n)@np.linalg.matrix_power(Z,m)@psi/2)
    print('Information: states, channels, discrimination, entropy, filters, correction and teleportation examples PASS')


if __name__=='__main__':
    algorithms();information()
