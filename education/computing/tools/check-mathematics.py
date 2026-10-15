#!/usr/bin/env python3
"""Numerically verify the worked circuit calculations (requires NumPy)."""
import numpy as np
from itertools import product
I=np.eye(2);H=np.array([[1,1],[1,-1]])/np.sqrt(2);X=np.array([[0,1],[1,0]]);Z=np.diag([1,-1]);zero=np.array([1,0]);one=np.array([0,1])
def close(a,b):assert np.allclose(a,b,atol=1e-10),(a,b)
def cx(n,c,t):
 m=np.zeros((2**n,2**n))
 for x in range(2**n):m[x^(1<<(n-1-t)) if x&(1<<(n-1-c)) else x,x]=1
 return m
def local(n,q,u):
 a=np.array([1.])
 for i in range(n):a=np.kron(a,u if q==i else I)
 return a
close(H@H,I)
for a,b in product([0,1],repeat=2):
 nand=lambda x,y:1-x*y
 t=nand(a,b);u=nand(a,t);v=nand(b,t)
 assert nand(u,v)==a^b
close(cx(2,0,1)@np.kron(H,I)@np.kron(zero,zero),np.array([1,0,0,1])/np.sqrt(2))
# Every computational output in the illustrated four-item circuit.
cz=np.diag([1,1,1,-1]);hh=np.kron(H,H);xx=np.kron(X,X)
s=np.ones(4)/2;D=2*np.outer(s,s)-np.eye(4)
close(hh@xx@cz@xx@hh,-D)
close(abs(hh@xx@cz@xx@hh@cz@s)**2,[0,0,0,1])
# All four function oracles for Deutsch.
for f in product([0,1],repeat=2):
 u=np.zeros((4,4))
 for x,y in product([0,1],repeat=2):u[2*x+(y^f[x]),2*x+y]=1
 out=np.kron(H,I)@u@hh@np.kron(zero,one)
 close([sum(abs(out[:2])**2),sum(abs(out[2:])**2)],[1,0] if f[0]==f[1] else [0,1])
# Teleportation with complex amplitudes: all four conditioned corrections.
psi=np.array([np.sqrt(.3),np.exp(.73j)*np.sqrt(.7)])
bell=np.array([1,0,0,1])/np.sqrt(2)
out=local(3,0,H)@cx(3,0,1)@np.kron(psi,bell)
for m,n in product([0,1],repeat=2):
 branch=out[2*(2*m+n):2*(2*m+n)+2]
 close(np.linalg.norm(branch)**2,.25)
 close(np.linalg.matrix_power(Z,m)@np.linalg.matrix_power(X,n)@branch*2,psi)
# General amplification agrees with the two-dimensional formula for all steps.
for N in [4,8,16]:
 for M in range(1,N):
  s=np.ones(N)/np.sqrt(N);o=np.diag([-1]*M+[1]*(N-M));d=2*np.outer(s,s)-np.eye(N);v=s.copy();theta=np.arcsin(np.sqrt(M/N))
  for k in range(8):
   close(sum(abs(v[:M])**2),np.sin((2*k+1)*theta)**2);v=d@o@v
print('Verified NAND XOR, H², Bell preparation, diffusion, four Deutsch oracles, all teleportation outcomes, and amplification probabilities.')

# The complex square root of NOT preserves norm as well as squaring to X.
root_x=np.array([[1+1j,1-1j],[1-1j,1+1j]])/2
close(root_x@root_x,X)
close(root_x.conj().T@root_x,I)
# Coarse measurement preserves coherence inside a degenerate eigenspace.
v=np.ones(3)/np.sqrt(3);p0=np.diag([1,1,0]);coherent=p0@v/np.sqrt(2/3)
plus3=np.array([1,1,0])/np.sqrt(2)
close(np.linalg.norm(p0@v)**2,2/3)
close(abs(np.vdot(plus3,coherent))**2,1)
close(plus3@np.diag([.5,.5,0])@plus3,.5)
# Ignoring Alice's outcome gives the same local state in either basis.
plus=(zero+one)/np.sqrt(2);minus=(zero-one)/np.sqrt(2)
close((np.outer(plus,plus)+np.outer(minus,minus))/2,I/2)
# The wrong kickback target remains unchanged and conveys no function value.
for f in product([0,1],repeat=2):
 u=np.zeros((4,4))
 for x,y in product([0,1],repeat=2):u[2*x+(y^f[x]),2*x+y]=1
 close(u@np.kron(plus,plus),np.kron(plus,plus))
# Appendix D: effects are positive, complete, and never give a false conclusive result.
c=1/(1+1/np.sqrt(2));e0=c*np.outer(minus,minus);ep=c*np.outer(one,one);eq=I-e0-ep
assert np.linalg.eigvalsh(eq).min()>-1e-10
close(plus@e0@plus,0);close(zero@ep@zero,0)
print('Verified square root of NOT, coarse measurement, local ensembles, wrong-target kickback, and inconclusive discrimination.')
