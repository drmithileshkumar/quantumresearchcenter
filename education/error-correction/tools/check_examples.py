#!/usr/bin/env python3
"""Independent finite-code and circuit certificates for the course. Requires NumPy."""
import itertools
import math
import numpy as np


def pauli(word):
    n = len(word)
    x = sum(1 << i for i,c in enumerate(word) if c in 'XY')
    z = sum(1 << i for i,c in enumerate(word) if c in 'YZ')
    return x | (z << n)


def commute(a, b, n):
    mask = (1 << n) - 1
    return (((a & mask) & (b >> n)).bit_count() + ((a >> n) & (b & mask)).bit_count()) % 2 == 0


def syndrome(e, checks, n):
    return tuple(int(not commute(e, g, n)) for g in checks)


def basis(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length()-1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return pivots


def in_span(value, pivots):
    while value:
        p = value.bit_length()-1
        if p not in pivots:
            return False
        value ^= pivots[p]
    return True


def errors(n, weight):
    for sites in itertools.combinations(range(n), weight):
        for labels in itertools.product('XYZ', repeat=weight):
            word = ['I']*n
            for site,label in zip(sites,labels):
                word[site] = label
            yield pauli(''.join(word))


def certify(checks, n, k, d):
    assert all(commute(a,b,n) for a,b in itertools.combinations(checks,2))
    pivots = basis(checks)
    assert len(pivots) == n-k
    # This binary test checks distance modulo phase. Explicit generators all have
    # positive phases and their independence/relations are separately known.
    found = None
    for weight in range(1,d+1):
        for e in errors(n,weight):
            if not any(syndrome(e,checks,n)) and not in_span(e,pivots):
                found = weight
                break
        if found is not None:
            break
    assert found == d, (n,found,d)


def cnot(n,c,t):
    u = np.zeros((2**n,2**n),dtype=complex)
    for i in range(2**n):
        j = i ^ (1 << (n-1-t)) if i & (1 << (n-1-c)) else i
        u[j,i] = 1
    return u


def main():
    five = [pauli(s) for s in ['XZZXI','IXZZX','XIXZZ','ZXIXZ']]
    certify(five,5,1,3)
    syndromes = [syndrome(e,five,5) for e in errors(5,1)]
    assert len(set(syndromes)) == 15 and all(any(s) for s in syndromes)
    assert syndrome(pauli('IXIII'),five,5) == (1,0,0,0)
    assert syndrome(pauli('ZIIII'),five,5) == (1,0,1,0)
    rows = ['1010101','0110011','0001111']
    checks = [pauli(''.join(label if bit=='1' else 'I' for bit in row)) for label in 'XZ' for row in rows]
    certify(checks,7,1,3)
    singles = [syndrome(e,checks,7) for e in errors(7,1)]
    assert len(set(singles)) == 21 and all(any(s) for s in singles)
    h = [int(row[::-1],2) for row in rows]
    space = {0}
    for row in h:
        space |= {v ^ row for v in list(space)}
    assert sorted(v.bit_count() for v in space) == [0]+[4]*7
    assert (1<<7)-1 not in space
    # Periodic L=3 lattice, qubits on horizontal then vertical edges.
    L=3; n=2*L*L
    def horizontal(x,y): return (x%L)+L*(y%L)
    def vertical(x,y): return L*L+(x%L)+L*(y%L)
    stars=[]; faces=[]
    for x,y in itertools.product(range(L),repeat=2):
        stars.append(sum(1<<i for i in [horizontal(x,y),horizontal(x-1,y),vertical(x,y),vertical(x,y-1)]))
        faces.append(sum(1<<i for i in [horizontal(x,y),vertical(x+1,y),horizontal(x,y+1),vertical(x,y)]) << n)
    assert len(basis(stars))==8 and len(basis(faces))==8
    certify(stars+faces,n,2,3)
    winding = sum(1<<horizontal(x,0) for x in range(L)) << n
    assert not any(syndrome(winding,stars+faces,n)) and not in_span(winding,basis(stars+faces))
    print('PASS: [[5,1,3]], [[7,1,3]], and [[18,2,3]] commutation, rank, and exhaustive distance certificates.')

    # Actual circuit operators, including coherent input superpositions.
    zero=np.array([1,0],complex); plus=np.array([1,1],complex)/np.sqrt(2)
    parity=cnot(3,1,2) @ cnot(3,0,2)
    bell=np.array([1,0,0,1],complex)/np.sqrt(2)
    out=parity @ np.kron(bell,zero)
    assert np.allclose(out[::2],bell) and np.allclose(out[1::2],0)
    out=parity @ np.kron(np.kron(plus,plus),zero)
    assert np.isclose(np.linalg.norm(out[::2])**2,0.5)
    assert np.allclose(out[::2]*np.sqrt(2),bell)
    odd=np.array([0,1,1,0],complex)/np.sqrt(2)
    assert np.allclose(out[1::2]*np.sqrt(2),odd)
    X=np.array([[0,1],[1,0]],complex);Z=np.diag([1,-1]);I=np.eye(2)
    u=cnot(2,0,1)
    for incoming,expected in [(np.kron(X,I),np.kron(X,X)),(np.kron(Z,I),np.kron(Z,I)),(np.kron(I,X),np.kron(I,X)),(np.kron(I,Z),np.kron(Z,Z))]:
        assert np.allclose(u@incoming@u.conj().T,expected)
    t=np.exp(1j*np.pi/4); T=np.diag([1,t]); S=np.diag([1,1j]); magic=np.array([1,t])/np.sqrt(2)
    for data in [zero,plus,np.array([np.sqrt(3)/2,1j/2])]:
        out=u @ np.kron(data,magic)
        assert np.isclose(np.linalg.norm(out[::2])**2,0.5)
        assert np.isclose(np.linalg.norm(out[1::2])**2,0.5)
        assert np.allclose(out[::2]*np.sqrt(2),T@data)
        assert np.allclose(S@out[1::2]*np.sqrt(2),t*(T@data))
    # Additional circuit figures: encoder, full two-ancilla recovery, X parity,
    # controlled-P stabilizer readout, and the four-edge hook-error example.
    def local(n, site, gate):
        result=np.array([[1]],complex)
        for j in range(n): result=np.kron(result,gate if j==site else I)
        return result
    H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
    data=np.array([np.sqrt(3)/2,1j/2])
    encoder=cnot(3,0,2)@cnot(3,0,1)
    encoded=encoder@np.kron(data,np.kron(zero,zero))
    expected=np.zeros(8,complex);expected[0]=data[0];expected[7]=data[1]
    assert np.allclose(encoded,expected)
    parity_x=local(3,2,H)@cnot(3,2,1)@cnot(3,2,0)@local(3,2,H)
    for outcome in (0,1):
        assert np.allclose(parity_x[outcome::2,0::2],(np.eye(4)+(-1)**outcome*np.kron(X,X))/2)
    extraction=cnot(5,2,4)@cnot(5,1,4)@cnot(5,1,3)@cnot(5,0,3)
    for site,result in [(None,0),(0,2),(1,3),(2,1)]:
        damaged=encoded if site is None else local(3,site,X)@encoded
        output=extraction@np.kron(damaged,np.kron(zero,zero))
        branch=output[result::4]
        assert np.isclose(np.linalg.norm(branch),1)
        repaired=branch if site is None else local(3,site,X)@branch
        assert np.allclose(repaired,encoded)
    def controlled(n,control,target,gate):
        p0=np.diag([1,0]);p1=np.diag([0,1])
        return local(n,control,p0)+local(n,control,p1)@local(n,target,gate)
    check=local(6,5,H)
    for row,gate in [(0,X),(1,Z),(2,Z),(3,X)]:
        check=controlled(6,5,row,gate)@check
    check=local(6,5,H)@check
    g=np.kron(np.kron(np.kron(np.kron(X,Z),Z),X),I)
    for outcome in (0,1):
        assert np.allclose(check[outcome::2,0::2],(np.eye(32)+(-1)**outcome*g)/2)
    remaining=cnot(5,3,4)@cnot(5,2,4)
    propagated=remaining@local(5,4,Z)@remaining.conj().T
    assert np.allclose(propagated,local(5,2,Z)@local(5,3,Z)@local(5,4,Z))
    print('PASS: diagram circuits for encoding, syndrome recovery, X parity, XZZXI readout, and hook propagation.')
    print('PASS: parity extraction preserves coherence, CNOT propagation, and both corrected T-injection branches.')

    # Enumerate all repetition-code bit-flip patterns and their residual actions.
    for p in [0.01,0.1,0.2]:
        failure=0
        for bits in itertools.product([0,1],repeat=3):
            s=(bits[0]^bits[1],bits[1]^bits[2])
            correction={(0,0):(0,0,0),(1,0):(1,0,0),(1,1):(0,1,0),(0,1):(0,0,1)}[s]
            residual=tuple(a^b for a,b in zip(bits,correction))
            if residual==(1,1,1):
                w=sum(bits);failure+=p**w*(1-p)**(3-w)
        assert np.isclose(failure,3*p*p-2*p**3)
    per_round=lambda d: 0.1*(0.001/0.01)**((d+1)/2)
    distances=[d for d in range(3,31,2) if 1e8*per_round(d)<=0.01*(1+1e-12)]
    assert distances[0]==17 and 2*17**2-1==577 and 2*19**2-1==721
    assert np.isclose(1e8*per_round(19),0.001)
    p=0.001
    for expected in [1e-4,1e-6,1e-10]:
        p=100*p*p
        assert math.isclose(p,expected,rel_tol=1e-12)
    assert np.isclose(35*0.005**3,4.375e-6)
    print('PASS: logical-error enumeration, concatenation recurrence, and explicitly hypothetical resource estimates.')


if __name__=='__main__':
    main()
