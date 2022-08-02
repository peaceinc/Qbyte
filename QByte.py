from mpl_toolkits.mplot3d import Axes3D  # required import for some machines to render 3d projection
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import os
import subprocess
import json
import sys
import serial
from serial.tools import list_ports
import time
import math
import scipy.stats
import matplotlib.gridspec as gridspec
import warnings
from matplotlib.widgets import Button
import tkinter as tk
from astral import LocationInfo
import datetime
from astral.sun import sunrise,sunset
from urllib.request import urlopen as uReq
warnings.simplefilter('ignore')

###########CONFIGURE HERE###########

ColorZ = 1.65#Z-score in the QByte bitstream where colors change
RotZ = 1.85#Z-score in the QByte bitstream where rotation occurs

DotSize = 4444
wordsize = 36

NEDspeed = 250#Number of bytes to stream from the RNG each second
RandomSrc = 'trng'#'trng' = TrueRNG hardware (https://ubld.it/truerng_v3) ... 'prng' = pseudo RNG ... 'ipfs' = interplenetary file system (REQUIRED config for ipfs mode -> NEDspeed=250, SupHALO=True, TurboUse=True. RNG hardware is NOT required as it will pull the data remotely.)
SupHALO = True#Set to 'True' for full (8 bitstream) QByte processing. Not reccomended for slower computers.
TurboUse = False#Set to 'True' only if you have a TurboRNG (https://ubld.it/products/truerngpro) or are running with RandomSrc = 'ipfs'. If set to 'True' while RandomSrc = 'prng', pseudo RNG will be used to simulate TurboRNG.
#The TurboRNG acts as a reliable high-speed data source that neuromorphically entangles together the two hemispheres (4 devices on each) of the Q-Byte processing.
#trouble may occur if using Turbo without NEDs

IPFS_Estuary = True#if RandomSrc = 'ipfs', 'True' will pull from Estuary, 'False' will pull from web3.storage

Genome = False#set to 'True' to XOR with genome from 23 and me data file (beta feature). Turns nucleotide information (A,G,C,T) into bits that factor in to the QByte output.
GenomeSrc = 'GenomeSample.txt'#Genome source data (this is where you can upload your DNA file from 23 and Me), ignored if Genome = 'False'

MaxFileTime = 10800#number of seconds of data to store to an individual output file
PushEstuary = False#uploads data to Estuary at MaxFileTime interval, requires curl. REQUIRED config -> NEDspeed=250, SupHALO=True, TurboUse=True. Any RandomSrc may be used.
EstuaryCollection = '47334123-5caa-4d98-9440-3b2412579842'#'bfffcaab-d302-4bab-b0ed-552e450a2dc9'

autofreq = 600#how often to switch view in seconds if ran in 'auto' mode

###########END USER CONFIGURATION###########

try:
    mType = sys.argv[1]#static,auto,nye
except:
    mType = 'static'

try:
    Rmks = sys.argv[2]#remarks
except:
    Rmks = '_'



outpath = os.getcwd()

TurboSpeed = NEDspeed

if RandomSrc=='prng':
    HALO = False
else:
    HALO = True


starttime = int(time.time()*1000)
outfile = open('%s/QB_%d_0_%s.txt'%(outpath,int(starttime/1000),Rmks),'w')
cmtfile = open('%s/QB_%d_%s_C.txt'%(outpath,int(starttime/1000),Rmks),'w')

outfile.write('ColorZ: %f RotZ: %f RNG params: %s %s %s\n'%(ColorZ,RotZ,RandomSrc,HALO,TurboUse))

if SupHALO==True:
    NumNeds = 8
else:
    NumNeds = 4

DayStarted = starttime - (starttime%86400000)
StartXT = (starttime-DayStarted)/3600000


EX = NEDspeed*4
ColorThres = ColorZ * ((NEDspeed*8*0.25)**0.5)
RotThres = RotZ * ((NEDspeed*8*0.25)**0.5)


ActionNumC = math.ceil((ColorZ*((8*NEDspeed*0.25)**0.5))+(4*NEDspeed))
Pmod_Color = (scipy.stats.binom((NEDspeed*8),0.5).sf(ActionNumC-1))*2
ActionNumR = math.ceil((RotZ*((8*NEDspeed*0.25)**0.5))+(4*NEDspeed))
Pmod_Rot = (scipy.stats.binom((NEDspeed*8),0.5).sf(ActionNumR-1))*2


#create zoomed std arrays

ax1s_zoom=[]
ax1sN_zoom=[]
Rstd_zoom=[]
Mstd_zoom=[]

for a in range (0,60):
    ax1s_zoom.append(((a*NEDspeed*8*0.25)**0.5)*1.96)
    ax1sN_zoom.append(((a*NEDspeed*8*0.25)**0.5)*-1.96)
    Rstd_zoom.append(((a*Pmod_Rot*(1-Pmod_Rot))**0.5)*1.65)
    Mstd_zoom.append(((a*Pmod_Color*(1-Pmod_Color))**0.5)*1.65)


####

IpfsIdx = [0]
MetaIdx = [0]

def NewIPFS():
    
    if IPFS_Estuary == True:
        estuary_json = subprocess.check_output('curl -X GET -H "Authorization: Bearer EST99cd9b05-5075-47b4-9897-f702f2e2ba2dARY" https://api.estuary.tech/collections/content/%s'%EstuaryCollection, shell=True)
        estuary_arr = json.loads(estuary_json)
        latest_cid = estuary_arr[-1]["cid"]
        data = 'https://%s.ipfs.dweb.link'%latest_cid
    else:

        data = 'https://bafybeievaadn5wv7xlxdto5m7nqn34q7nzdk5x4fpdh4sogrx4xkdg5ad4.ipfs.dweb.link/short/NEDpredata_%d.txt'%IpfsIdx[0]
    

    #data = 'https://bafybeievaadn5wv7xlxdto5m7nqn34q7nzdk5x4fpdh4sogrx4xkdg5ad4.ipfs.dweb.link/short/NEDpredata_0.txt'
    #data = 'https://bafybeibkvizfujdlgn34lczqphlbopd423s5p7jutglhmajobpfo5o5o2y.ipfs.dweb.link'


    print('pulling data from %s'%data)
    
    uClient = uReq(data)
    page_html = str(uClient.read())
    uClient.close()
    sepfile = page_html.split('\\n')
    
    
    MetaXX=[]
    for a in range (0,len(sepfile)-1):
        if a==0:
            xandy = sepfile[a][2:].split(',')
        else:
            xandy = sepfile[a].split(',')
        
        if len(xandy)>5:

            uNed=[]
            for b in range (0,len(xandy)-2):
                uNed.append(int(xandy[b]))
            
            #print(uNed)

            MetaXX.append(uNed)
        
    IpfsIdx[0] += 1

    print(np.shape(MetaXX))

    

    return MetaXX

if RandomSrc=='ipfs':
    
    MetaNED = NewIPFS()
    

def GrabIPFS():
    if MetaIdx[0]>=len(MetaNED):
        xNED = NewIPFS()
        for a in range (0,len(xNED)):
            MetaNED[a] = xNED[a]
            
        MetaIdx[0] = 0
    
    grabbed = MetaNED[MetaIdx[0]]
    MetaIdx[0] += 1
    return grabbed
    
####


plt.style.use('dark_background')
#plt.grid([False])
fig = plt.figure(constrained_layout=True)
gs = fig.add_gridspec(3,2)
ax1 = fig.add_subplot(gs[:,0], projection='3d')
ax2 = fig.add_subplot(gs[0,1])
ax3 = fig.add_subplot(gs[1,1])
ax4 = fig.add_subplot(gs[2,1])
ax4t = ax4.twinx()

city = LocationInfo(latitude=37.7,longitude=-122.2)

riprise=[]
ripset=[]

zoomsto = [1]
viewsto = [3]
viewlong = [0]
entsto = [1]
SsnCt = [0]

for a in range (0,10):

    srise = sunrise(city.observer, date=datetime.datetime.now()+datetime.timedelta(days=a))
    sset = sunset(city.observer, date=datetime.datetime.now()+datetime.timedelta(days=a))
    riprise.append((srise.hour+(srise.minute/60))+(24*a))
    ripset.append((sset.hour+(sset.minute/60))+(24*a))
    
alltypes = ['hypercube','sphere','pyramid','AEM','quad']
    
def MkShape(shp):
    if shp == 'hypercube':
        
        WM_ll = 1.4
        WM_ul = 4.1
        
        #infile = 'SimulationsHC.txt'
    
        ShapeC = []
        Node=[]
        sNode = []
        
        readFile = open('%s/HypercubeExt.txt'%outpath,'r')
        sepfile = readFile.read().split('\n')
        for a in range (0,len(sepfile)):
            xandy = sepfile[a].split('\t')
            ShapeC.append([int(xandy[0])-4,int(xandy[1])-4,int(xandy[2])-4])
            Node.append(int(xandy[3]))
            if int(xandy[3])==1:
                sNode.append([int(xandy[0])-4,int(xandy[1])-4,int(xandy[2])-4])
                
    if shp == 'sphere' or shp == 'nye':
        
        WM_ll = 1.4
        WM_ul = 1.42
            
        #infile = 'Simulations_Sphere12.txt'
        ShapeC = []
        xxx=[]
        yyy=[]
        zzz=[]
        for a in range (0,12):
            theta = 2*np.pi*(a/12)
            numphi = int(np.abs(round(np.sin(theta)*12)))
            for b in range (0,numphi):
                phi = ((2*np.pi)/numphi)*b
                x = np.sin(theta)*np.cos(phi)
                y = np.sin(theta)*np.sin(phi)
                z = np.cos(theta)
                ShapeC.append([x,y,z])
                xxx.append(x)
                yyy.append(y)
                zzz.append(z)
        
        sNode = []; idxs=[]
        idx = np.argmin(xxx)
        idxs.append(idx)
        sNode.append(ShapeC[idx])
        idx = np.argmax(xxx)
        idxs.append(idx)
        sNode.append(ShapeC[idx])
        idx = np.argmin(yyy)
        idxs.append(idx)
        sNode.append(ShapeC[idx])
        idx = np.argmax(yyy)
        idxs.append(idx)
        sNode.append(ShapeC[idx])
        idx = np.argmin(zzz)
        idxs.append(idx)
        sNode.append(ShapeC[idx])
        idx = np.argmax(zzz)
        idxs.append(idx)
        sNode.append(ShapeC[idx])
        
        Node=[]
        for a in range (0,len(ShapeC)):
            if a in idxs:
                Node.append(1)
            else:
                Node.append(0)
                
        #print(np.amin(zzz),np.amax(zzz))
    
    
    if shp == 'pyramid':
        
        WM_ll = 0.7
        WM_ul = 2.1      
        
        #infile = 'SimulationsHC.txt'#temp
        ShapeC = []
        x = [1,2,3,4,5,0.5,0.5,0.5,0.5,0.5,1,2,3,4,5,5.5,5.5,5.5,5.5,5.5,2,3,4,1.5,1.5,1.5,2,3,4,4.5,4.5,4.5,2.5,3.5,3,3]
        y = [0.5,0.5,0.5,0.5,0.5,1,2,3,4,5,5.5,5.5,5.5,5.5,5.5,1,2,3,4,5,1.5,1.5,1.5,2,3,4,4.5,4.5,4.5,2,3,4,3,3,2.5,3.5]
        z = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3]
        z = np.array(z)-0.5
        
        Node = [1,0,1,0,1,1,0,1,0,1,1,0,1,0,1,1,0,1,0,1,1,0,1,1,0,1,1,0,1,1,0,1,1,1,1,1,1,0,1,0,1,0,0,0,0,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,1,1]
        
        plusX = [1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5]
        plusY = [1,1,1,1,1,2,2,2,2,2,3,3,3,3,3,4,4,4,4,4,5,5,5,5,5]
        plusZ = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #            [1,0,1,0,1,0,0,0,0,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,1]
        
        #cap and floor
        
        for a in range (0,len(x)):
            ShapeC.append([x[a],y[a],z[a]])
        for a in range (0,len(plusX)):
            ShapeC.append([plusX[a],plusY[a],plusZ[a]])
        ShapeC.append([3,3,3])    
    
        sNode = []
        for a in range (0,len(ShapeC)):
            if Node[a]==1:
                sNode.append(ShapeC[a])
    
    if shp=='AEM':
        
        WM_ll = 0.6
        WM_ul = 0.64    
        
        #infile = 'Simulations_AEM10.txt'
        ShapeC = []
        for a in range (0,10):
            rads = (a/10)*2*np.pi
            ShapeC.append([np.cos(rads),np.sin(rads),0])
        sNode = ShapeC
        Node = [1,1,1,1,1,1,1,1,1,1]
        
    if shp=='quad':
        
        WM_ll = 1.4
        WM_ul = 2.1  
        
        #infile = 'Simulations_AEM10.txt'#temporary!
        ShapeC = [[2,1,0],[2,5,0],[4,1,0],[4,5,0],[1,2,0],[1,4,0],[5,2,0],[5,4,0]]
        sNode = ShapeC
        Node = [1,1,1,1,1,1,1,1]
    
    infile = 'sim_%s'%shp

    SimMI = []    
    readFile = open('%s/%s.txt'%(outpath,infile),'r')
    sepfile = readFile.read().split('\n')
    for a in range (0,len(sepfile)-1):
        SimMI.append(float(sepfile[a]))
    Msorted = sorted(SimMI)
    
    
    Dist=[]
    WM = np.zeros((len(sNode),len(sNode)))
    ShapeCt = 0
    Kct = 0
    for a in range (0,len(ShapeC)):
        xm = []
        for b in range (0,len(sNode)):
            dd = (((ShapeC[a][0]-sNode[b][0])**2)+((ShapeC[a][1]-sNode[b][1])**2)+((ShapeC[a][2]-sNode[b][2])**2))**0.5
            if dd>0:
                xm.append(1/(dd**3))
            else:
                xm.append(999)
        if np.amax(xm)==999:#checks if we're on a sNode
            
            for b in range (0,len(sNode)):
                dd = (((ShapeC[a][0]-sNode[b][0])**2)+((ShapeC[a][1]-sNode[b][1])**2)+((ShapeC[a][2]-sNode[b][2])**2))**0.5
                if WM_ll<=dd<=WM_ul:#sqrt of 2 to 4 but within tolerance to allow floating point errors
                    WM[ShapeCt,b] = 1
                    Kct += 1
            ShapeCt += 1
                    
        Dist.append(xm)
    
    return ShapeC,sNode,Node,Msorted,Dist,WM
    
def newfile(n):
    global outfile
    outfile.close()

    if PushEstuary==True:
        try:
            estout = subprocess.check_output('curl -X POST https://shuttle-5.estuary.tech/content/add -H "Authorization: Bearer EST99cd9b05-5075-47b4-9897-f702f2e2ba2dARY" -H "Accept: application/json" -H "Content-Type: multipart/form-data" -F "data=@%s/QB_%d_%d_%s.txt"'%(outpath,int(starttime/1000),n-1,Rmks), shell=True)
            estjson = json.loads(estout)
            cid = estjson["cid"]
            eststr = 'curl -X POST https://api.estuary.tech/collections/add-content -d' + " '{ " + '"contents": [], "cids": ["' + cid + '"], "collection": "%s" }'%EstuaryCollection + "' -H " + '"Content-Type: application/json" -H "Authorization: Bearer EST99cd9b05-5075-47b4-9897-f702f2e2ba2dARY"'
            os.system('%s'%eststr)
        except:
            print("Estuary Upload %d_%d_%s Failed"%(int(starttime/1000),n-1,Rmks))

    outfile = open('%s/QB_%d_%d_%s.txt'%(outpath,int(starttime/1000),n,Rmks),'w')

def printInput():
    inp = inputtxt.get(1.0, "end-1c")
    cmtfile.write('%d,%s\n'%(int(time.time()*1000),inp))
    cmtfile.flush()
    os.fsync(cmtfile.fileno())
    frame.wm_withdraw()
    inputtxt.delete(1.0,"end-1c")
    
def kill(self):
    ani.event_source.stop()
    outfile.close()
    cmtfile.close()
    sys.exit()

def comment(self):
    frame.wm_deiconify()
    frame.mainloop()
    
def zoom(self):
    tmp = zoomsto[0]
    if tmp==0:
        zoomsto[0] = 1
    else:
        zoomsto[0] = 0
        

def autoview():
    tmp = viewsto[0]
    if tmp==(len(alltypes)-1):
        viewsto[0] = 0
    else:
        viewsto[0] += 1
        
    mShapeC[viewsto[0]] = MkShape(alltypes[viewsto[0]])[0]
    
    viewlong.append(viewsto[0])
    
    AC = Bulk()
    AimColors.append(GetColors(AC[0],viewsto[0])[0])
    AC = Bulk()
    AimColors.append(GetColors(AC[0],viewsto[0])[0])
    
    outfile.write('switch view to %d\n'%viewsto[0])
        
def view(self):
    autoview()

def entrain(self):
    global ult_t
    global MaxFileTime
    SsnCt[0]+=1
    tmp = entsto[0]
    if tmp==0:
        entsto[0] = 1
        newfile(int(len(ult_t)/MaxFileTime))
        bent.color = '0.5'
    else:
        entsto[0] = 0
        newfile(-1*int((SsnCt[0]/2)+0.5))
        bent.color = 'red'
    
    
    

    
frame = tk.Tk()
frame.title("eh?")
frame.geometry('400x50')
inputtxt = tk.Text(frame,height = 1,width = 35)
inputtxt.pack()
printButton = tk.Button(frame,text = "Submit", command = printInput)
printButton.pack()

axcmt = plt.axes([0.05, 0.05, 0.07, 0.05])
bcmt = Button(axcmt, 'comment', color = '0.5', hovercolor='0.8')
bcmt.on_clicked(comment)

axkil = plt.axes([0.13, 0.05, 0.07, 0.05])
bkil = Button(axkil, 'stop', color = '0.5', hovercolor='0.8')
bkil.on_clicked(kill)

axzoom = plt.axes([0.21, 0.05, 0.07, 0.05])
bzoom = Button(axzoom, 'zoom', color = '0.5', hovercolor='0.8')
bzoom.on_clicked(zoom)

axview = plt.axes([0.29, 0.05, 0.07, 0.05])
bview = Button(axview, 'view', color = '0.5', hovercolor='0.8')
bview.on_clicked(view)

axent = plt.axes([0.37, 0.05, 0.07, 0.05])
bent = Button(axent, 'entrain', color = '0.5', hovercolor='0.8')
bent.on_clicked(entrain)


AllLO=[]
Readfile=open('%s/Wordbank.txt'%outpath,encoding='latin-1')
Lines=Readfile.read().split('\n')
for line in range(0,len(Lines)):
    AllLO.append(Lines[line])


if Genome==True:
    GenomeBin = ['CC','CG','CA','CT','GC','GG','GA','GT','AC','AG','AA','AT','TC','TG','TA','TT']
    Readfile = open('%s/%s'%(outpath,GenomeSrc),'r')
    sepfile = Readfile.read().split('\n')
    PreSeq = []
    for a in range (21,len(sepfile)):
        for b in range (0,len(GenomeBin)):
            if GenomeBin[b] in sepfile[a]:
                PreSeq.append(b)
    GenomeBits = []
    for a in range (0,len(PreSeq),2):
        GenomeBits.append((PreSeq[a]*16)+PreSeq[a+1])

    # print(np.amin(GenomeBits),np.amax(GenomeBits),len(GenomeBits))
    



if RandomSrc=='trng':

    
    
    ports=dict()  
    ports_avaiable = list(list_ports.comports())
    
    
    rngcomports = []
    turbocom = None
    
    for temp in ports_avaiable:
        if HALO==True:
        	if temp[1].startswith("TrueRNG"):
        		if 'pro' in temp[1]:
        			print ('found pro')
        			turbocom = str(temp[0])
        		else:
        			print('Found:           ' + str(temp))
        			rngcomports.append(str(temp[0]))
        else:
        	if temp[1].startswith("TrueRNG"):
        		print ('found device')
        		turbocom = str(temp[0])
            
    if HALO==True:
        ser = []            
        for a in range(0,len(rngcomports)):
        	ser.append (serial.Serial(port=rngcomports[a],timeout=10))    
    if TurboUse==True:
        turboser= (serial.Serial(port=turbocom,timeout=10)) 
    
    
               
    #print('Using com port:  ' + str(rng1_com_port))
    #print('Using com port:  ' + str(rng2_com_port))
    #print('==================================================')
    sys.stdout.flush()
    
    if HALO==True:
        for a in range(0,len(rngcomports)):
        	if(ser[a].isOpen() == False):
        		ser[a].open()
        
        	ser[a].setDTR(True)
        	ser[a].flushInput()
    if TurboUse==True:
        if turboser.isOpen()==False:
            turboser.open()
        turboser.setDTR(True)
        turboser.flushInput()
        
        sys.stdout.flush()
else:
    rngcomports = ['pseudoRNG']
    ser = ['pseudoRNG']



def M2P(MIv,typidx):
    idx = 0
    for a in range (0,len(mMsorted[typidx])):
        if mMsorted[typidx][a]>MIv:
            idx += 1
    if idx==0:
        idx += 1
    p_i = idx/1000000
    #print(idx,MIv,np.amin(Msorted),np.amax(Msorted))
    return p_i
    
    




def Bulk():
    
    pct = []
    allsums=[]
    

    
    for a in range (0,9):
        pct.append([])
        
    if TurboUse==True:
    
        if RandomSrc=='trng':
            turboser.flushInput()
            supernode = turboser.read(TurboSpeed)#CHG
        if RandomSrc=='ipfs':
            supernode = GrabIPFS()
        if RandomSrc=='prng':
            supernode = np.random.randint(0,256,TurboSpeed)
            
        tempsum = 0
        for b in range (0,len(supernode)):
            outfile.write('%d,'%(supernode[b]))
            pct[8].append(supernode[b])
            
            
            #allnodes.append(supernode[b])
            strnode = str(bin(256+int(supernode[b])))[3:]
            tempsum += (int(strnode[0])+int(strnode[1])+int(strnode[2])+int(strnode[3])+int(strnode[4])+int(strnode[5])+int(strnode[6])+int(strnode[7]))
        outfile.write('%d,T\n'%(int(time.time()*1000)))
        
        allsums.append(tempsum)
        
    for a in range(0,NumNeds):
        if (HALO==True or TurboUse==False) and RandomSrc=='trng':
            try:
                ser[a%len(ser)].flushInput()
                node = ser[a%len(ser)].read(NEDspeed)
            except:
                node = []
        else:
            if RandomSrc=='trng':
                node = turboser.read(NEDspeed)
            if RandomSrc=='prng':
                node = np.random.randint(0,256,NEDspeed)
            if RandomSrc=='ipfs':
                node = GrabIPFS()
        #print (a,len(node),TotalRuns)
        while len(node)==0:
            print('BAD READ ON %s ... removing'%rngcomports[a%len(ser)])
            ser.remove(ser[a%len(ser)])
            #bads[a] += 1
            try:
                ser[a%len(ser)].flushInput()
                node = ser[a%len(ser)].read(NEDspeed)
            except:
                node = []
       
        tempsum = 0
        for mm in range (0,NEDspeed):
            outfile.write('%d,'%(node[mm]))
            strnum = bin(256+node[mm])[3:]
            pct[a].append(node[mm])
            
            strnode = str(strnum)
            tempsum += (int(strnode[0])+int(strnode[1])+int(strnode[2])+int(strnode[3])+int(strnode[4])+int(strnode[5])+int(strnode[6])+int(strnode[7]))
        allsums.append(tempsum)
        outfile.write('%d,%s\n'%(int(time.time()*1000),rngcomports[a%len(ser)]))
        
    x = []#CHG should be NEDspeed long
    
    Pur0 = pct[0]
    Pur1 = pct[1]
    Pur2 = pct[2]
    Pur3 = pct[3]
    Pur4 = pct[4]
    Pur5 = pct[5]
    Pur6 = pct[6]
    Pur7 = pct[7]
    if TurboUse==True:
        PurT = pct[8]
    
    #This is where the magic occurs:
    GenomeIdx = ((Pur0[0]*(256**2)) + (Pur0[1]*(256**1)) + (Pur0[2]*(256**0)))

    for b in range (0,len(Pur0)):
        
        if SupHALO==True:
            xA = Pur0[b]^Pur7[b]
            xB = Pur1[b]^Pur6[b]
            xC = Pur2[b]^Pur5[b]
            xD = Pur3[b]^Pur4[b]
        
            xE = xA^xD
            xF = xB^xC
        else:
        
            xE = Pur0[b]^Pur3[b]
            xF = Pur1[b]^Pur2[b]
        
        xG = xE^xF
        
        if TurboUse==True:
            xH = xG^PurT[b]
        else:
            xH = xG

        if Genome==True:
            GenomeIdxX = (GenomeIdx+b)%len(GenomeBits)
            xDNA = xH ^ GenomeBits[GenomeIdxX]
        else:
            xDNA = xH
        
        x.append(xDNA)

        
        
        
        


    

    
    #OG:
    #ser.flushInput()
    #x = ser.read(NEDspeed)
    
    bitct = 0
    for a in range (0,len(x)):
        outfile.write('%d,'%x[a])
        strnode = str(bin(256+int(x[a])))[3:]
        bitct += int(strnode[0])+int(strnode[1])+int(strnode[2])+int(strnode[3])+int(strnode[4])+int(strnode[5])+int(strnode[6])+int(strnode[7])        
        
    outfile.write('%d,QBYTE | '%(int(time.time()*1000)))
    
    
    
    outfile.flush()
    os.fsync(outfile.fileno())
    
    
    str0 = str(bin(256+int(x[-2])))[3:] + str(bin(256+int(x[-1])))[3:]
    ones = int(str0[0])+int(str0[1])+int(str0[2])+int(str0[3])+int(str0[4])+int(str0[5])+int(str0[6])+int(str0[7])+int(str0[8])+int(str0[9])+int(str0[10])+int(str0[11])+int(str0[12])+int(str0[13])+int(str0[14])+int(str0[15])

    #cat = np.random.randint(0,3)
    
    uidx = -3
    sector = -9999
    while sector < -1:
        if x[uidx] < 252:
            sector = x[uidx]%3
        uidx -= 1
    
    
    
    LO_idx = ((sector%3)*65536)+(x[-2]*256)+x[-1]
    wrd = AllLO[LO_idx]

    Z = np.abs(ones-8)

    if ones==8:
        symbol = '.0'
    if ones<8:
        symbol = '.-%d'%Z
    if ones>8:
        symbol = '.+%d'%Z

    outfile.write('%s\n'%wrd)
        
    #print(len(x))
    
    return x,bitct,symbol,wrd,allsums

maxon = 65535
def GetColors(colors,typidx):
    #colors,r1 = Bulk()
    offset = 0
    Config = []
    U=[]
    V=[]
    for lights in range (0,len(msNode[typidx])):
        slider = (colors[-1+offset]*256)+colors[-2+offset]
        uidx = -3+offset
        sector = -9999
        while sector < -1:
            if colors[uidx] < 252:
                sector = colors[uidx]%6
            uidx -= 1
            
        offset = uidx
        
        
        if sector == 0:
            R,G,B = maxon,slider,0
        if sector == 1:
            R,G,B = slider,maxon,0
        if sector == 2:
            R,G,B = 0,maxon,slider
        if sector == 3:
            R,G,B = 0,slider,maxon
        if sector == 4:
            R,G,B = slider,0,maxon
        if sector == 5:
            R,G,B = maxon,0,slider
        Config.append([R,G,B])
        
        theta = (np.pi*(1/3)*sector)+((slider/65536)*np.pi*(1/3))
        U.append(np.cos(theta))
        V.append(np.sin(theta))
        
    return Config,sector,U,V



#shape initialization:
if mType == 'nye':
    targettime = int(sys.argv[3])
RadList = []
for a in range (0,10):
    rads = (a/10)*2*np.pi
    RadList.append(rads)
BaseX = [0,6,6,0,0]
BaseY = [0,0,6,6,0]
BaseZ = [0,0,0,0,0]
Beam1x = [0,3,6]
Beam1y = [0,3,6]
Beam1z = [0,3,0]
Beam2x = [6,3,0]
Beam2y = [0,3,6]
Beam2z = [0,3,0]
pollX = [0,0]
pollY = [0,0]
pollZ = [-6,0]

mShapeC=[]
OGShapeC=[]
msNode=[]
mNode=[]
mMsorted=[]
mDist=[]
mWM=[]
for a in range (0,len(alltypes)):
    print('building %s'%alltypes[a])
    info = MkShape(alltypes[a])
    mShapeC.append(info[0])
    OGShapeC.append(info[0])
    msNode.append(info[1])
    mNode.append(info[2])
    mMsorted.append(info[3])
    mDist.append(info[4])
    mWM.append(info[5])






    
def RotateAEM(theta,typidx):
    for a in range (0,len(mShapeC[typidx])):
        mShapeC[typidx][a][0] = np.cos(RadList[a]+theta)
        mShapeC[typidx][a][1] = np.sin(RadList[a]+theta)
        RadList[a] = RadList[a]+theta
    
def Rotate(theta,axs,typidx,doall=False):
    if axs=='x':
        m0 = 2
        m1 = 0
        m2 = 1
    if axs=='y':
        m0 = 0
        m1 = 1
        m2 = 2
    if axs=='z':
        m0 = 1
        m1 = 0
        m2 = 2
    for a in range (0,len(mShapeC[typidx])):
        if (-1<=mShapeC[typidx][a][m0]<=1 and doall==False) or doall==True:
            r = ((mShapeC[typidx][a][m1]**2)+(mShapeC[typidx][a][m2]**2))**0.5
            #phi = np.arctan((ShapeC[a][1])/(ShapeC[a][0]))
            phi = math.atan2(mShapeC[typidx][a][m2],mShapeC[typidx][a][m1])
            phi += theta
            mShapeC[typidx][a][m1] = r*np.cos(phi)
            mShapeC[typidx][a][m2] = r*np.sin(phi)

def Drop(typidx):
    for a in range (0,len(mShapeC[typidx])):
        mShapeC[typidx][a][2] = mShapeC[typidx][a][2]-0.1
            
def SnapInt(typidx):
    for a in range (0,len(mShapeC[typidx])):
        mShapeC[typidx][a][0] = int(np.rint(mShapeC[typidx][a][0]))
        mShapeC[typidx][a][1] = int(np.rint(mShapeC[typidx][a][1]))
        mShapeC[typidx][a][2] = int(np.rint(mShapeC[typidx][a][2]))



ult_t=[]
Mplt=[]
Mstd=[]
Rplt=[]
Rstd=[]

Xsums=[]
QBsums=[]

ax1y=[]
ax1s=[]
ax1sN=[]  
axQB=[]  
for a in range (0,NumNeds+1):
    Xsums.append([])
    ax1y.append([])

    
    
AimColors = []
Aim_t=[]

AC = Bulk()
AimColors.append(GetColors(AC[0],viewsto[0])[0])

AC = Bulk()
AimColors.append(GetColors(AC[0],viewsto[0])[0])

Aim_t.append(len(ult_t))

Rot_t=[-999]
RotTyp=[]

MI=[]
MIt=[]

KMlog=[]
CumP=[]


def GetI(uu,vv,typidx):
    Ksum=0.0; Kct=0; NCct=0
    for a in range (0,len(uu)):
        for b in range (0,len(uu)):
            if (mWM[typidx][a,b]==1):#detects neighboring cell, allowing for diagonal directions
                Ksum+= (((uu[a])*(uu[b]))+((vv[a])*(vv[b])))
                Kct+=1
            NCct+=1
            
    SSQ_K = len(uu)
    MORAN = ((len(uu)*Ksum)/(float(Kct)*float(SSQ_K)))
    return MORAN


def animate(i):
    

    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()
    ax4t.clear()

    if len(ult_t)%MaxFileTime==0 and len(ult_t)>0 and entsto[0]==1:
        newfile(int(len(ult_t)/MaxFileTime))
    
    reds=[]
    greens=[]
    blues=[]
    
    now_p = time.time()
    now = now_p-(starttime/1000)
    
    if mType=='auto':
        if len(ult_t)%autofreq==0 and len(ult_t)>0:
            autoview()
    
    useview = viewsto[0]
    
    Type = alltypes[useview]
    

    
    if mType=='nye':
        timetodest = targettime - now_p
    else:
        timetodest = None
        
    hrOfD = int((now_p%86400)/3600)
    mnOfD = int((now_p%3600)/60)
    scOfD = int(now_p%60)
    fOfD = str(now_p%1) + '000000'
    microf = fOfD[2:8]
    
    hrRun = int((now)/3600)
    mnRun = int((now%3600)/60)
    scRun = int(now%60)
    
    AC = Bulk()
    t_symbol = AC[2]
    Bird = AC[3]
    
    for a in range (0,len(AC[4])):
        Xsums[a].append(AC[4][a])
    
    
    
    pos = len(ult_t)-Aim_t[-1]
    #print('op enter %d'%pos)
    
    if (np.abs(AC[1]-EX)>ColorThres) and (pos>10):
        aim = GetColors(AC[0],useview)
        
        AimColors.append(aim[0])
        Aim_t.append(len(ult_t))
        #print('spike i %d'%pos)
        
        ival = GetI(aim[2],aim[3],useview)
        tmp_p = M2P(ival,useview)
        pval = 1/tmp_p
        
        x_red = []
        x_green = []
        x_blue = []
        for a in range (0,len(aim[0])):
            x_red.append(aim[0][a][0])
            x_green.append(aim[0][a][1])
            x_blue.append(aim[0][a][2])
        outfile.write('color change,%f,%d,%d,%d,%d,%f\n'%(ival,useview,int(np.average(x_red)/256),int(np.average(x_green)/256),int(np.average(x_blue)/256),pval))
        MI.append(pval)
        MIt.append((int(now_p*1000)-DayStarted)/3600000)
        KMlog.append(np.log(tmp_p))
        CumP.append(scipy.stats.chi2.sf((np.sum(KMlog)*-2),(2*len(MIt))))
        
        #print(ival)
        
        
        

        
    pos = len(ult_t)-Aim_t[-1]
    #print(pos)
        
    if (pos <= 10):
        Ucolors = []
        for a in range (0,len(msNode[useview])):
            Rnow = AimColors[-1][a][0]
            Rprv = AimColors[-2][a][0]
            Rdo = ((Rnow-Rprv)*(pos/10))+Rprv
    
            Gnow = AimColors[-1][a][1]
            Gprv = AimColors[-2][a][1]
            Gdo = ((Gnow-Gprv)*(pos/10))+Gprv
    
            Bnow = AimColors[-1][a][2]
            Bprv = AimColors[-2][a][2]
            Bdo = ((Bnow-Bprv)*(pos/10))+Bprv
            
            Ucolors.append([Rdo,Gdo,Bdo])
    else:
        Ucolors = AimColors[-1]
        
    Rpos = len(ult_t)-Rot_t[-1]
    if (np.abs(AC[1]-EX)>RotThres) and (Rpos>10):
        Rot_t.append(len(ult_t))
        RotTyp.append(GetColors(AC[0],useview)[1])
        outfile.write('rotation\n')
    Rpos = len(ult_t)-Rot_t[-1]
    if Rpos < 10 and (Type=='hypercube'):
        if Type=='hypercube':
            allbool = False
        else:
            
            allbool = True
        if RotTyp[-1]==0:
            Rotate(np.pi/20,'x',useview,doall=allbool)
        if RotTyp[-1]==1:
            Rotate(-np.pi/20,'x',useview,doall=allbool)
        if RotTyp[-1]==2:
            Rotate(np.pi/20,'y',useview,doall=allbool)
        if RotTyp[-1]==3:
            Rotate(-np.pi/20,'y',useview,doall=allbool)
        if RotTyp[-1]==4:
            Rotate(np.pi/20,'z',useview,doall=allbool)
        if RotTyp[-1]==5:
            Rotate(-np.pi/20,'z',useview,doall=allbool)
        if Rpos==9 and Type=='hypercube':
            SnapInt(useview)
    if Rpos < 10 and Type=='AEM':
        if 0<=RotTyp[-1]<=2:
            RotateAEM(np.pi/30,useview)
        else:
            RotateAEM(np.pi/-30,useview)

    
    if Type =='nye' and 0<=timetodest<=60:
        Drop(useview)
        
    NowXT = (int(now_p*1000)-DayStarted)/3600000
    ult_t.append(NowXT)
    NodeCt=0
    
    #print(useview,Type,np.shape(Ucolors))
    
    for a in range (0,len(mShapeC[useview])):
        if mNode[useview][a]==1:
            red = Ucolors[NodeCt][0]/(256**2)
            green = Ucolors[NodeCt][1]/(256**2)
            blue = Ucolors[NodeCt][2]/(256**2)
            NodeCt += 1
            reds.append(red)
            greens.append(green)
            blues.append(blue)
            if Type=='quad':
                if a<4:
                    mkr = '|'
                else:
                    mkr = '_'
                ax1.scatter(mShapeC[useview][a][0],mShapeC[useview][a][1],mShapeC[useview][a][2],color=[red,green,blue],edgecolors=None,s=DotSize*2,marker=mkr)
            else:
                ax1.scatter(mShapeC[useview][a][0],mShapeC[useview][a][1],mShapeC[useview][a][2],color=[red,green,blue],edgecolors=None,s=DotSize)
    for a in range (0,len(mShapeC[useview])):
        if mNode[useview][a]==0:
            red = np.average(reds,weights=mDist[useview][a])
            green = np.average(greens,weights=mDist[useview][a])
            blue = np.average(blues,weights=mDist[useview][a])
            ax1.scatter(mShapeC[useview][a][0],mShapeC[useview][a][1],mShapeC[useview][a][2],color=[red,green,blue],edgecolors=None,s=DotSize)
            
            
    M = len(AimColors)-(2*len(viewlong))
    if pos <= 10:
        Nt = (len(ult_t)-(10*M)+(10-pos))-11
    else:
        Nt = (len(ult_t)-(10*M))-11
        
    R = len(RotTyp)
    if Rpos <= 10:
        NtR = (len(ult_t)-(10*R)+(10-Rpos))-11
    else:
        NtR = (len(ult_t)-(10*R))-11
    
    Mplt.append(M - (Pmod_Color*Nt))
    Mstd.append(((Nt*Pmod_Color*(1-Pmod_Color))**0.5)*1.65)
    
    Rplt.append(R - (Pmod_Rot*NtR))
    Rstd.append(((NtR*Pmod_Rot*(1-Pmod_Rot))**0.5)*1.65)
            
    plt.suptitle('%02d:%02d:%02d.%s%s UTC      |      T+ %02d:%02d:%02d'%(hrOfD,mnOfD,scOfD,microf,t_symbol,hrRun,mnRun,scRun),color=[np.average(reds),np.average(greens),np.average(blues)],size=wordsize)
    if Type == 'AEM':
        ax1.text(0,0,0,"%s"%(Bird),ha='center',va='center',color=[np.average(reds),np.average(greens),np.average(blues)],size=wordsize)
    if Type == 'quad':
        ax1.text(3,3,0,"%s"%(Bird),ha='center',va='center',color=[np.average(reds),np.average(greens),np.average(blues)],size=wordsize)
      
        
        
    ax1.grid(False)
    ax1.set_axis_off()
    if Type=='nye':
        ax1.plot(pollX,pollY,pollZ,color='white')
        ax1.set_xlim3d(-3.5,3.5)
        ax1.set_ylim3d(-3.5,3.5)
        ax1.set_zlim3d(-6.5,0.5)
        hoursleft = int(timetodest/3600)
        minleft = int(timetodest/60)%60
        secleft = int(timetodest%60)
        #plt.suptitle('%02d:%02d:%02d'%(hoursleft,minleft,secleft),size=70)
        Rotate(np.pi/20,'x',useview,doall=True)
        
    
    
    


            
    QBsums.append(AC[1])
    axQB.append(np.sum(QBsums)-(len(ult_t)*NEDspeed*8*0.5))
    for a in range (0,len(Xsums)):
        ax1y[a].append(np.sum(Xsums[a])-(len(ult_t)*NEDspeed*8*0.5))
        #print(a,(np.sum(Xsums[a])-(len(ult_t)*NEDspeed*8*0.5)))
    ax1s.append(((len(ult_t)*NEDspeed*8*0.25)**0.5)*1.96)
    ax1sN.append(((len(ult_t)*NEDspeed*8*0.25)**0.5)*-1.96)
    
    if zoomsto[0]==1:
        if TurboUse==True:
            ax2.plot(ult_t,ax1y[0],color='red',linewidth='1',label='Turbo')
            for a in range (1,len(ax1y)):
                ax2.plot(ult_t,ax1y[a],color='lightgray',linewidth='1')
        else:
            for a in range (0,len(ax1y)-1):
                ax2.plot(ult_t,ax1y[a],color='lightgray',linewidth='1')
        ax2.plot(ult_t,axQB,color='magenta',linewidth='1',label='Qbyte')
        ax2.plot(ult_t,ax1s,color='aqua',linestyle='--')
        ax2.plot(ult_t,ax1sN,color='aqua',linestyle='--')      
        ax3.plot(ult_t,Mplt,color='aqua',label='color change')
        ax3.plot(ult_t,Mstd,color='aqua',linestyle='--')
        ax3.plot(ult_t,Rplt,color='red',label='rotation')
        ax3.plot(ult_t,Rstd,color='red',linestyle='--')
        
        for a in range (0,len(riprise)):
            if StartXT<=riprise[a]<=NowXT:
                ax2.axvline(x=riprise[a],color='lightblue')
                ax3.axvline(x=riprise[a],color='lightblue')
        for a in range (0,len(ripset)):
            if StartXT<=ripset[a]<=NowXT:
                ax2.axvline(x=ripset[a],color='pink')
                ax3.axvline(x=ripset[a],color='pink')


    else:
                
        
        if TurboUse==True:
            ax2.plot(ult_t[-60:],np.array(ax1y[0][-60:])-ax1y[0][-60],color='red',linewidth='1',label='Turbo')
            for a in range (1,len(ax1y)):
                ax2.plot(ult_t[-60:],np.array(ax1y[a][-60:])-ax1y[a][-60],color='lightgray',linewidth='1')
        else:
            for a in range (0,len(ax1y)-1):
                ax2.plot(ult_t[-60:],np.array(ax1y[a][-60:])-ax1y[a][-60],color='lightgray',linewidth='1')
        ax2.plot(ult_t[-60:],np.array(axQB[-60:])-axQB[-60],color='magenta',linewidth='1',label='Qbyte')
        ax2.plot(ult_t[-60:],ax1s_zoom,color='aqua',linestyle='--')
        ax2.plot(ult_t[-60:],ax1sN_zoom,color='aqua',linestyle='--')      
        ax3.plot(ult_t[-60:],np.array(Mplt[-60:])-Mplt[-60],color='aqua',label='color change')
        ax3.plot(ult_t[-60:],Mstd_zoom,color='aqua',linestyle='--')
        ax3.plot(ult_t[-60:],np.array(Rplt[-60:])-Rplt[-60],color='red',label='rotation')
        ax3.plot(ult_t[-60:],Rstd_zoom,color='red',linestyle='--')

    
    
    ax4.plot(MIt,MI)
    ax4.set_yscale('log')
    ax4t.plot(MIt,CumP,color='red')
    ax4t.set_ylim([0,1])
    
    ax2.legend(loc=2)
    ax3.legend(loc=2)
    
    ax2.set_ylabel('raw deviations')
    ax3.set_ylabel('events')
    ax4.set_ylabel('Color Coherence 1/p (L) cum p (R)')

    
    if Type == 'pyramid':
        ax1.plot(BaseX,BaseY,BaseZ,color='white')
        ax1.plot(Beam1x,Beam1y,Beam1z,color='white')
        ax1.plot(Beam2x,Beam2y,Beam2z,color='white')
        
    
        
                
ani = animation.FuncAnimation(fig, animate, interval=1000)

plt.show()
