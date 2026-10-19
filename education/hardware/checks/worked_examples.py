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
    # Two-stage readout: compare a conditional-probability expansion and inversion.
    for p1 in np.linspace(0,1,11):
        observed=.03*(1-p1)+.93*p1
        assert_allclose((observed-.03)/.90,p1,atol=1e-14)
    # Quartic oscillator matrix elements give the stated transmon correction.
    a=np.diag(np.sqrt(np.arange(1,12)),1)
    coordinate=a+a.T
    fourth=np.linalg.matrix_power(coordinate,4)
    for n in range(6):assert_allclose(fourth[n,n],6*n*n+6*n+3)
    # Compare low transmon gaps with a charge-basis diagonalization, independently
    # of the quartic spectrum used for the figure.
    charge=np.arange(-35,36)
    ec,ej=.25,20.
    h=np.diag(4*ec*charge**2)-ej/2*(np.eye(71,k=1)+np.eye(71,k=-1))
    levels=np.linalg.eigvalsh(h)
    assert_allclose(levels[1]-levels[0],np.sqrt(8*ec*ej)-ec,rtol=.01)
    # Dispersive shift as the small-coupling limit of an avoided crossing.
    detuning,g=200.,10.
    shift=np.sqrt((detuning/2)**2+g*g)-detuning/2
    assert_allclose(shift,g*g/detuning,rtol=.003)
    # Large-detuning Raman elimination: eigenvalue splitting of the full matrix.
    delta,o1,o2=100.,1.,1.
    raman=np.array([[0,0,o1/2],[0,0,o2/2],[o1/2,o2/2,delta]])
    values=np.linalg.eigvalsh(raman)
    assert_allclose(values[1]-values[0],o1*o2/(2*delta),rtol=.001)
    # Full nine-state Rydberg pulse simulation checks all four computational phases.
    ir=np.array([[0,0,0],[0,0,1],[0,1,0]],complex)
    rr=np.zeros((9,9));rr[8,8]=1
    hc=np.kron(ir,np.eye(3))/2+1000*rr
    ht=np.kron(np.eye(3),ir)/2+1000*rr
    blockade=evolution(hc,np.pi)@evolution(ht,2*np.pi)@evolution(hc,np.pi)
    code=[0,1,3,4]
    assert_allclose(blockade[np.ix_(code,code)],np.diag([1,-1,-1,-1]),atol=.004)
    # Single-loss binomial code: same norm and distinguishable error states.
    a=np.diag(np.sqrt(np.arange(1,7)),1)
    logical=np.zeros((7,2));logical[[0,4],0]=1/np.sqrt(2);logical[2,1]=1
    assert_allclose(logical.T@(a.T@a)@logical,2*I,atol=1e-14)
    assert_allclose(logical.T@a@logical,np.zeros((2,2)),atol=1e-14)
    loss=a@logical
    parity=np.diag((-1.)**np.arange(7))
    assert_allclose(parity@logical,logical)
    assert_allclose(parity@loss,-loss)
    # Majorana algebra and order dependence of neighboring ideal exchanges.
    gammas=[np.kron(X,I),np.kron(Y,I),np.kron(Z,X),np.kron(Z,Y)]
    for j,gj in enumerate(gammas):
        for k,gk in enumerate(gammas):
            assert_allclose(gj@gk+gk@gj,(2 if j==k else 0)*np.eye(4),atol=1e-14)
    u12=(np.eye(4)+gammas[0]@gammas[1])/np.sqrt(2)
    u23=(np.eye(4)+gammas[1]@gammas[2])/np.sqrt(2)
    assert_allclose(u12.conj().T@u12,np.eye(4),atol=1e-14)
    assert np.linalg.norm(u12@u23-u23@u12)>1
    # Mean coherence while awaiting a geometric link, checked by direct summation.
    attempts=np.arange(1,30000)
    success,step=.01,.001
    direct=np.sum(success*(1-success)**(attempts-1)*np.exp(-attempts*step))
    closed=success*np.exp(-step)/(1-(1-success)*np.exp(-step))
    assert_allclose(direct,closed,rtol=1e-12)
    assert_allclose((1-.9**10)*.95**4,.5305054812982992)
    assert_allclose(3*.02**2-2*.02**3,.001184)
    assert_allclose(1-.05**(1/10000),.0002995283597766)
    print('PASS: driven evolution, ZZ and exchange gates, preparation, readout, decoherence, platform estimates, parity extraction, transmon perturbation, Raman elimination, Rydberg phases, binomial loss syndromes, Majorana algebra, and resource statistics.')

if __name__=='__main__':main()
