# This import registers the 3D projection, but is otherwise unused.
#from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
import numpy as np
#import matplotlib.animation as animation
import os
import sys
#import serial
#from serial.tools import list_ports
#import time
import math
import scipy.stats
#import matplotlib.gridspec as gridspec
import warnings
#from matplotlib.widgets import Button
#import tkinter as tk
#from astral import LocationInfo
#import datetime
#from astral.sun import sunrise,sunset
warnings.simplefilter('ignore')



outpath = os.getcwd()

anlzfile = [sys.argv[1]]

for a in range (0,len(anlzfile)):
    readFile = open('%s\%s'%(outpath,anlzfile[a]),'r')
    if a==0:
        sepfile = readFile.read().split('\n')
    else:
        sepfile += readFile.read().split('\n')[1:]
    readFile.close()

head = sepfile[0].split(' ')
ColorZ = float(head[1])
RotZ = float(head[3])
firstline = sepfile[1].split(',')
if firstline[-1]=='T':
    TurboUse = True
else:
    TurboUse = False
NEDspeed = len(firstline)-2
rngs = 1
rngct = 0
while rngct==0:
    line = sepfile[rngs+1]
    if 'QBYTE' in line:
        rngct += 1
    else:
        rngs += 1
        

        
print(rngs,NEDspeed,TurboUse,ColorZ,RotZ)#next is auto input readM



ActionNumC = math.ceil((ColorZ*((8*NEDspeed*0.25)**0.5))+(4*NEDspeed))
Pmod_Color = (scipy.stats.binom((NEDspeed*8),0.5).sf(ActionNumC-1))*2
ActionNumR = math.ceil((RotZ*((8*NEDspeed*0.25)**0.5))+(4*NEDspeed))
Pmod_Rot = (scipy.stats.binom((NEDspeed*8),0.5).sf(ActionNumR-1))*2

alltypes = ['hypercube','sphere','pyramid','AEM','quad']

Msuite = []
for a in range (0,len(alltypes)):
    infile = 'sim_%s'%alltypes[a]
    SimMI = []
    readFileM = open('%s\%s.txt'%(outpath,infile),'r')
    sepfileM = readFileM.read().split('\n')[:-1]
    for a in range (0,len(sepfileM)):
        SimMI.append(float(sepfileM[a]))
    Msorted = sorted(SimMI)
    Msuite.append(Msorted)
    readFileM.close()




def M2P(MIv,ix):
    idx = 0
    for a in range (0,len(Msuite[ix])):
        if Msuite[ix][a]>MIv:
            idx += 1
    if idx==0:
        idx += 1
    p_i = idx/1000000
    return p_i




ult_t=[]
ult_sums=[]
ax1y=[]
for a in range (0,rngs+1):
    ult_sums.append([])
    ax1y.append([])

ax1s=[]
ax1sN=[]

MIt=[]
MIp=[]
CumP=[]

colorsave=[]
rotsave=[]

colorct=0
rotct = 0

Mplt=[]
Mstd=[]
Rplt=[]
Rstd=[]

KMlog = 0

ult_tt=[]

for a in range (0,len(sepfile)):
    if 'QBYTE' in sepfile[a]:#goal: get bitsums. EE can be read. hopefully retrieve code for good read_lights code. so yeah anlz dep on LV..
              
        bitct = 0
        xandy = sepfile[a].split(',')
        for b in range (0,len(xandy)-2):            
            strnode = str(bin(256+int(xandy[b])))[3:]
            bitct += int(strnode[0])+int(strnode[1])+int(strnode[2])+int(strnode[3])+int(strnode[4])+int(strnode[5])+int(strnode[6])+int(strnode[7])
        
        ult_sums[0].append(bitct)
        
        ult_t.append((int(xandy[-2])-1622530800000)/86400000)

        
        for b in range (1,rngs+1):
            bitct = 0
            xandy = sepfile[a-b].split(',')
            for c in range (0,len(xandy)-2):            
                strnode = str(bin(256+int(xandy[c])))[3:]
                bitct += int(strnode[0])+int(strnode[1])+int(strnode[2])+int(strnode[3])+int(strnode[4])+int(strnode[5])+int(strnode[6])+int(strnode[7])
            ult_sums[b].append(bitct)
        colorsave.append(colorct)
        rotsave.append(rotct)
    if 'color' in sepfile[a]:
        MIt.append(ult_t[-1])
        ival = float(sepfile[a].split(',')[1])
        shp = int(sepfile[a].split(',')[2])
        pval = M2P(ival,shp)
        MIp.append(1/(pval))
        
        KMlog += np.log(pval)
        CumP.append(scipy.stats.chi2.sf((KMlog*-2),(2*len(MIt))))
        
        colorct += 1
        
    if 'rotation' in sepfile[a]:
        rotct += 1
        
    if a%10000==0:
        print("processing line %d of %d"%(a,len(sepfile)))
    
        

for a in range (0,len(ult_t)):
    Nt = (a-(10*colorsave[a]))-11
    Mplt.append(colorsave[a] - (Pmod_Color*Nt))
    Mstd.append(((Nt*Pmod_Color*(1-Pmod_Color))**0.5)*1.65)
    
    NtR = (a-(10*rotsave[a]))-11
    Rplt.append(rotsave[a] - (Pmod_Rot*NtR))
    Rstd.append(((NtR*Pmod_Rot*(1-Pmod_Rot))**0.5)*1.65)
    if a%10000==0:
        print("b ... processing line %d of %d"%(a,len(ult_t)))

cumsum = np.zeros(len(ax1y))

for a in range (0,len(ult_t)):
    for b in range (0,len(ax1y)):
        
        ax1y[b].append(cumsum[b]-((a)*NEDspeed*8*0.5))
        
        cumsum[b] += ult_sums[b][a]
        
        
    ax1s.append((((a)*NEDspeed*8*0.25)**0.5)*1.96)
    ax1sN.append((((a)*NEDspeed*8*0.25)**0.5)*-1.96)
    if a%10000==0:
        print("c ... processing line %d of %d"%(a,len(ult_t)))
        
    

plt.style.use('dark_background')
#plt.grid([False])
fig = plt.figure(constrained_layout=True)
#gs = fig.add_gridspec(3,2)
#ax1 = fig.add_subplot(gs[:,0], projection='3d')
ax2 = fig.add_subplot(311)
ax3 = fig.add_subplot(312)
ax4 = fig.add_subplot(313)
    

#Q,T,1234...,
ax2.plot(ult_t,ax1y[0],color='magenta',linewidth='1',label='Qbyte')
if TurboUse==True:
    ax2.plot(ult_t,ax1y[1],color='red',linewidth='1',label='Turbo')
    for a in range (2,len(ax1y)):
        ax2.plot(ult_t,ax1y[a],color='lightgray',linewidth='1')
else:
    for a in range (1,len(ax1y)):
        ax2.plot(ult_t,ax1y[a],color='lightgray',linewidth='1')

ax2.plot(ult_t,ax1s,color='aqua',linestyle='--')
ax2.plot(ult_t,ax1sN,color='aqua',linestyle='--')

ax2.legend(loc=2)

ax3.plot(ult_t,Mplt,color='aqua',label='color change')
ax3.plot(ult_t,Mstd,color='aqua',linestyle='--')
ax3.plot(ult_t,Rplt,color='red',label='rotation')
ax3.plot(ult_t,Rstd,color='red',linestyle='--')
ax3.legend(loc=2)
ax4.plot(MIt,MIp,color='aqua')
ax4.set_ylabel('Color Coherence 1/p (L) cum p (R)')
ax4.set_yscale('log')
ax4t = ax4.twinx()
ax4t.plot(MIt,CumP,color='red')
ax4t.set_ylim([0,1])




    
ax2.set_ylabel('raw deviations')
ax3.set_ylabel('events')

    

    
tLb=[]
tAx = np.arange(int(np.amin(ult_t)),int(np.amax(ult_t))+2,1/24)
for a in range (0,len(tAx)):
    tLb.append('%d'%(a%24))
    
u_tAx=[]
u_tLb=[]
for a in range (0,len(tAx)):
    if np.amin(ult_t)<=tAx[a]<=np.amax(ult_t):
        u_tAx.append(tAx[a])
        u_tLb.append(tLb[a])

ax4.set_xlim([np.amin(ult_t),np.amax(ult_t)])
ax4t.set_xlim([np.amin(ult_t),np.amax(ult_t)])
ax3.set_xlim([np.amin(ult_t),np.amax(ult_t)])
ax2.set_xlim([np.amin(ult_t),np.amax(ult_t)])

    
ax4.set_xticks(u_tAx)
ax4.set_xticklabels(u_tLb)
ax4t.set_xticks(u_tAx)
ax4t.set_xticklabels(u_tLb)
ax2.set_xticks([])
ax3.set_xticks([])


plt.show()

