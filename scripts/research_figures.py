#!/usr/bin/env python3
"""Rebuild original research plots with NumPy and Matplotlib (optional authoring tools)."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/assets'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.labelsize':12,'svg.fonttype':'none','svg.hashsalt':'qrc-research','savefig.facecolor':'white'})
BLUE='#246593'; ORANGE='#a64d26'; PURPLE='#765391'
def save(name,draw):
 fig,ax=plt.subplots(figsize=(6.0,3.7),layout='constrained')
 draw(ax)
 ax.grid(alpha=.14);ax.set_axisbelow(True)
 fig.savefig(OUT/(name+'.svg'),metadata={'Date':None,'Creator':'Quantum Research Center'})
 plt.close(fig)
def decoherence(ax):
 n=np.arange(0,101)
 ax.plot(n,.9**n,color=BLUE,label='Record overlap 0.9 per fragment')
 ax.set(xlabel='Number of environment fragments N',ylabel='Remaining coherence factor',ylim=(-.02,1.04))
 ax.legend(frameon=False,fontsize=10)
def correlations(ax):
 v=np.linspace(0,1,200)
 ax.plot(v,4*v,color=BLUE,label='Noisy box: S = 4v')
 ax.axhline(2,color=ORANGE,ls='--',label='Local bound: 2')
 ax.axhline(2*np.sqrt(2),color=PURPLE,ls=':',label='Quantum bound: 2√2')
 ax.set(xlabel='Box visibility v',ylabel='CHSH value S',xlim=(0,1),ylim=(0,4.2))
 ax.legend(frameon=False,fontsize=10)
def search(ax):
 n=64;k=np.arange(25);theta=np.arcsin(1/np.sqrt(n))
 ax.plot(k,np.sin((2*k+1)*theta)**2,'o-',color=BLUE,ms=4,label='One marked item among 64')
 ax.set(xlabel='Oracle iterations k',ylabel='Success probability',ylim=(-.03,1.06))
 ax.legend(frameon=False,fontsize=10)
def capacity(ax):
 p=np.linspace(0,1,200)
 ax.plot(p,np.maximum(0,1-2*p),color=BLUE,lw=2)
 ax.scatter([.25],[.5],color=ORANGE,zorder=3)
 ax.annotate('p = 0.25: 0.5 qubits/use',(.25,.5),xytext=(.34,.66),arrowprops={'arrowstyle':'->','color':ORANGE},fontsize=10)
 ax.set(xlabel='Erasure probability p',ylabel='Unassisted quantum capacity',ylim=(-.03,1.05))
def control(ax):
 m=np.arange(201);eps=.01;q=np.sin(eps/2)**2
 ax.plot(m,np.sin(m*eps/2)**2,color=BLUE,label='Fixed coherent rotation')
 ax.plot(m,(1-(1-2*q)**m)/2,color=ORANGE,ls='--',label='Independent stochastic flips')
 ax.set(xlabel='Repeated cycles m',ylabel='Probability of the minus outcome')
 ax.legend(frameon=False,fontsize=10)
def sensing(ax):
 # Gamma = 1 fixes time units. Information is normalized by N*T.
 t=np.linspace(.001,1.6,400);n=10
 ax.plot(t,t*np.exp(-2*t),color=BLUE,label='Product probes')
 ax.plot(t,n*t*np.exp(-2*n*t),color=PURPLE,ls='--',label='Entangled probes, N = 10')
 ax.axhline(1/(2*np.e),color='#89949e',lw=1,ls=':')
 ax.set(xlabel='Interrogation time γt',ylabel='Total information × γ / (NT)')
 ax.legend(frameon=False,fontsize=10)
if __name__=='__main__':
 OUT.mkdir(exist_ok=True)
 for name,draw in [('environment-records',decoherence),('correlation-bounds',correlations),('search-rotation',search),('erasure-capacity',capacity),('coherent-control',control),('noisy-sensing',sensing)]:save(name,draw)
 print('Built six original research plots.')
