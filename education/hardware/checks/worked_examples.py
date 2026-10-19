#!/usr/bin/env python3
"""Independent small-model checks for the hardware manuscript (NumPy only)."""
import numpy as np
from numpy.testing import assert_allclose

X=np.array([[0,1],[1,0]],complex)
Y=np.array([[0,-1j],[1j,0]],complex)
Z=np.diag([1,-1]);I=np.eye(2)
def evolution(h,t):
    values,vectors=np.linalg.eigh(h)
    return (vectors*np.exp(-1j*values*t))@vectors.conj().T

def main():
    # Compare the analytic detuned formula with direct Hamiltonian evolution.
    for detuning in [0,.4,1,3]:
        for t in np.linspace(0,9,31):
            observed=abs(evolution((detuning*Z+X)/2,t)[1,0])**2
            expected=np.sin(np.sqrt(1+detuning**2)*t/2)**2/(1+detuning**2)
            assert_allclose(observed,expected,atol=1e-12)
    # Controlled phase including the explicitly stated local rotations.
    U=evolution(np.kron(Z,Z)/2,np.pi/2)
    rz=evolution(Z/2,-np.pi/2)
    corrected=np.kron(rz,rz)@U
    assert_allclose(corrected/corrected[0,0],np.diag([1,1,1,-1]),atol=1e-12)
    # Exchange generates equal-magnitude amplitudes, and Heisenberg gives SWAP.
    exchange=evolution((np.kron(X,X)+np.kron(Y,Y))/2,np.pi/4)
    assert_allclose(abs(exchange[:,1])**2,[0,.5,.5,0],atol=1e-12)
    heisenberg=(np.kron(X,X)+np.kron(Y,Y)+np.kron(Z,Z))/4
    swap=evolution(heisenberg,np.pi)
    ideal=np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]])
    assert_allclose(swap/swap[0,0],ideal,atol=1e-12)
    assert_allclose(1/(1+np.exp(5)),.006692850924)
    assert_allclose(.02+(1-.02-.02)*.8,.788)
    assert_allclose(1/(1/(2*100)+1/100),66.6666666667)
    assert_allclose(np.sqrt(8*20*.25)-.25,6.07455532034)
    assert_allclose(1/(1+20**2),1/401)
    # HOM: permanent of the balanced two-mode transformation vanishes.
    B=np.array([[1,1],[1,-1]])/np.sqrt(2)
    coincidence=B[0,0]*B[1,1]+B[0,1]*B[1,0]
    assert_allclose(coincidence,0,atol=1e-12)
    assert_allclose(1-.9**10,.6513215599)
    assert_allclose(.999**1000,.367695424771)
    assert_allclose(1-.05**.001,.0029912495451)
    # Parity extraction preserves coherence of a Bell pair with the auxiliary 0.
    circuit=np.zeros((8,8))
    for x in range(2):
        for y in range(2):
            for a in range(2):circuit[4*x+2*y+(a^x^y),4*x+2*y+a]=1
    bell=np.zeros(8);bell[[0,6]]=1/np.sqrt(2)
    assert_allclose(circuit@bell,bell)
    for x in range(2):
        for y in range(2):assert circuit[4*x+2*y+(x^y),4*x+2*y]==1
    print('PASS: driven evolution, ZZ and exchange gates, preparation, readout, decoherence, platform estimates, parity extraction, and resource statistics.')

if __name__=='__main__':main()
