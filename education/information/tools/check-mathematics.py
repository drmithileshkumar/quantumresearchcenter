#!/usr/bin/env python3
"""Independent finite checks for the expanded Information lessons; requires NumPy."""
from math import sqrt, pi
import numpy as np

I=np.eye(2, dtype=complex)
zero,one=I[:,0],I[:,1]
X=np.array([[0,1],[1,0]], dtype=complex)
Z=np.diag([1,-1])
H=(X+Z)/sqrt(2)
plus,minus=H[:,0],H[:,1]


def same(a,b):
    assert np.allclose(a,b,atol=1e-12,rtol=1e-12),(a,b)


def outer(v):
    return np.outer(v,v.conj())


def h(q):
    return -sum(p*np.log2(p) for p in (q,1-q) if p>0)


def entropy(rho):
    return -sum(p*np.log2(p) for p in np.linalg.eigvalsh(rho) if p>1e-14)


def main():
    # Conditioning and an observation that improves inference but not decision score.
    for prior,expected in ((.75,.8),(.9,.9)):
        joint=np.array([[prior*.2,prior*.8],[(1-prior)*.8,(1-prior)*.2]])
        same(joint.sum(),1);same(np.max(joint,axis=0).sum(),expected)
    same(1.75,.5*1+.25*2+.125*3+.125*3)
    same(h(.25),.8112781244591328)
    # Interference, global phase, and density matrices for different ensembles.
    for phase in np.linspace(0,2*pi,33):
        psi=np.array([1,np.exp(1j*phase)])/sqrt(2)
        same(abs((H@psi)[0])**2,(1+np.cos(phase))/2)
        same(outer(np.exp(1j*phase)*plus),outer(plus))
    mix=(outer(zero)+outer(plus))/2
    same(mix,[[.75,.25],[.25,.25]]);same(np.linalg.det(mix),.125)
    bell=np.array([1,0,0,1])/sqrt(2)
    bell_minus=np.array([1,0,0,-1])/sqrt(2)
    same(np.kron(H,H)@bell_minus,[0,1/sqrt(2),1/sqrt(2),0])
    # Sequential generalized measurement: the instrument, not just the POVM.
    M0=np.diag([sqrt(3)/2,.5]);M1=np.diag([.5,sqrt(3)/2])
    branch=M0@plus
    same(np.vdot(branch,branch),.5)
    same(branch/np.linalg.norm(branch),[sqrt(3)/2,.5])
    same(np.linalg.norm(M0@branch)**2,5/16)
    output=sum(M@outer(plus)@M.conj().T for M in (M0,M1))
    same(np.vdot(plus,output@plus),(1+sqrt(3)/2)/2)
    # Analytic readout optimum compared with a separate matrix-eigenvalue solution.
    for p in np.linspace(.01,.99,37):
        theta=np.arctan2(-(1-p),p)/2
        v=np.array([np.cos(theta),np.sin(theta)])
        score=p*abs(np.vdot(v,zero))**2+(1-p)*(1-abs(np.vdot(v,plus))**2)
        difference=p*outer(zero)-(1-p)*outer(plus)
        optimum=(1+sum(abs(np.linalg.eigvalsh(difference))))/2
        same(score,optimum)
    pair_delta=(outer(np.kron(zero,zero))-outer(np.kron(plus,plus)))/2
    same((1+sum(abs(np.linalg.eigvalsh(pair_delta))))/2,(1+sqrt(3)/2)/2)
    # Dense coding: encode on the first wire, then CNOT followed by H.
    cx=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
    for a in (0,1):
        for b in (0,1):
            encoded=np.kron(np.linalg.matrix_power(X,b)@np.linalg.matrix_power(Z,a),I)@bell
            decoded=np.kron(H,I)@cx@encoded
            same(abs(decoded)**2,np.eye(4)[2*a+b])
    # Compression must preserve signals, not only their average matrix.
    signals=[np.array([sqrt(3)/2,sign*.5]) for sign in (1,-1)]
    average=sum(outer(v) for v in signals)/2
    same(average,np.diag([.75,.25]))
    for v in signals:same(np.vdot(v,average@v),5/8)
    same(.75**3+3*.25*.75**2,54/64)
    # A filter's complete branch account.
    for p in (.5,.75,.9):
        state=np.array([sqrt(p),0,0,sqrt(1-p)])
        K=np.diag([sqrt((1-p)/p),1]);L=np.diag([sqrt((2*p-1)/p),0])
        same(K.conj().T@K+L.conj().T@L,I)
        success=np.kron(K,I)@state
        same(np.linalg.norm(success)**2,2*(1-p))
        same(success/np.linalg.norm(success),bell)
    # Erasure branches and their entropies, calculated as actual joint matrices.
    erasure=np.array([0,0,1],complex);embed=np.array([[1,0],[0,1],[0,0]])
    for e in (.1,.25,.5,.75):
        retained=np.kron(I,embed)@bell
        rb=(1-e)*outer(retained)+e*np.kron(I/2,outer(erasure))
        output=np.trace(rb.reshape(2,3,2,3),axis1=0,axis2=2)
        same(entropy(rb),h(e)+e);same(entropy(output),h(e)+1-e)
        same(entropy(output)-entropy(rb),1-2*e)
    same(1-2*h(.05),.4272060857680875)
    print('PASS: conditioning, coding, interference, ensembles, sequential measurement, optimal decisions, dense coding, compression, filters, erasure entropies, and ideal key-rate arithmetic.')


if __name__=='__main__':
    main()
