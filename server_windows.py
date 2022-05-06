#socket_echo_server.py

import socket
import sys
import struct

#from generic_controller import updatecontrols

from pylab import *
import pandas as pd


import numpy as np


# notes pour plus tard au sujet de CONTAM
# les INTEGER sont en NETWORK BYTES (BIG ENDIAN Symbole:  ! )
# les FLOAT sont au format de la machine (--> pour le moment: LITTLE, symbole = '<')

def readheader(connection):

    data=connection.recv(8) #header
    headerbytes=data
    data=connection.recv(4)
    messagelen = struct.unpack("!i", data)[0]
    
    #data=connection.recv(4) #pad
    data=connection.recv(4) #section number
    section = struct.unpack("!i", data)[0]
    data=connection.recv(4) # 9 check

    data=connection.recv(messagelen-20)
        
    return(section,data)

def readtimeinfo(data): #s==2
    for i in range(int(len(data)/4)):
        imin=i*4
        intval=struct.unpack("!i", data[imin:imin+4])[0]
        if (i==0):
            startday=intval
        if (i==1):
            endday=intval
                
    dt=intval # time step is the last of this integer serie
    maxtime=(endday-startday+1)*86400

    return(dt,maxtime,startday)

def readcontaminants(data): #s==3
    ncont=struct.unpack("!i", data[0:4])[0]
    contids=[]
    
    for i in range(ncont):
        imin=4+i*4
        contids.append(struct.unpack("!i", data[imin:imin+4])[0])
        
    names=data[imin+4:].decode('utf-8').split('\x00')
    names.remove('') # last separator is kept as emtpy
    # I may use a dictionnary, would be easier

    #print("Contaminant names",names)
    
    return(names)

def readzones(data): #s==3
    nz=struct.unpack("!i", data[0:4])[0]
    levels=[]
    ahs=[]
    volume=[]
    
    imin=4
    for i in range(nz):
        levels.append(struct.unpack("!i", data[imin:imin+4])[0])
        imin+=4

    for i in range(nz):
        ahs.append(struct.unpack("!i", data[imin:imin+4])[0])
        imin+=4

    for i in range(nz):
        # WARNING: documentation indicates volume as INT, but it is clearly FLOAT, I tested it
        volume.append(struct.unpack("<f", data[imin:imin+4])[0])
        imin+=4

        
    names=data[imin:].decode('utf-8').split('\x00')
    names.remove('') # last separator is kept as emtpy
    # I may use a dictionnary, would be easier

    #print("Zone names",names)
    
    return(names)


def recv1contaminant(data,nzones): # section 120 (!! writen 100 in doucmentation, but wrong)

    currenttime=struct.unpack("!i", data[0:4])[0]

    
    #Linux   - imin=8 # = 8 car je pense qu'entre 4 et 8 il y a une pad0 qui ne sert a rien
    #Windows - imin=4 # = 
    imin=4
    
    #print("len ",ncont,nzones)
    agentid=struct.unpack("!i", data[imin:imin+4])[0]
    imin+=4
    concentration=[]

    
    for z in range(nzones):
        concentration.append(struct.unpack("<f", data[imin:imin+4])[0])
        imin+=4

    #print ("data ",data)
    #print ("test",currenttime,agentid,concentration)
    
    return(agentid,concentration)
    
    


def contamready(data): # section 0
    currenttime=struct.unpack("!i", data[0:4])[0]
    return currenttime


def advance(option,nexttime,connection): #section 20
    #option 8: control message update
    
       header=b'ACATMSG'
       data=struct.pack("!8s",header)

       tosend=data

       lendata=28
       data=struct.pack("!i",lendata)
       tosend=tosend+data
                
       #pad=0
       #data=struct.pack("!i",pad)
       #tosend=tosend+data #pad...
                
       messagetype=20
       data=struct.pack("!i",messagetype)
       tosend=tosend+data
                
       version=9
       data=struct.pack("!i",version)
       tosend=tosend+data
                
               
       data=struct.pack("!i",option)
       tosend=tosend+data
                
       #pad=0
       #data=struct.pack("!i",pad)
       #tosend=tosend+data #pad...
                
       data=struct.pack("!i",nexttime)
       tosend=tosend+data

       connection.sendall(tosend)

       

def readcontrols(data): #s==5
    nnodes=struct.unpack("!i", data[0:4])[0]

    nid=[]
    nval=[]
    nname=[]
                
    for i in range(nnodes):
        imin=(i+1)*4
        nodeid=struct.unpack("!i", data[imin:imin+4])[0]
        nid.append(nodeid)

        imin=(nnodes+1)*4+i*4
        nodeval=struct.unpack("<f",data[imin:imin+4])[0]
        nval.append(nodeval)


    names=data[imin+4:].decode('utf-8').split('\x00')
    names.remove('') # last separator is kept as emtpy
    # I may use a dictionnary, would be easier

    #print ("Name","appearance order","message id")
    #for i in range(nnodes):
    #    print (names[i],i+1,nid[i])
        
    
    # IMPORTANT NOTE: in CONTAM documentation it is said that these ID (nodeid) are used to
    # indentify the control nodes in CONTAMX, and that they could be different from the
    # displayed values in CONTAMW sketchpad.
    # In practice, I see that this nodeid is in fact the same value as in CONTAMW, but
    # that internally, they are number in sequential order of apparence. 

    
    return(nid,names,nval)
    

def writecontrol(ctrlid,value,connection):
    header=b'ACATMSG'
    data=struct.pack("<8s",header)

    tosend=data

    lendata=28
    data=struct.pack("!i",lendata)
    tosend=tosend+data
                
    #pad=0
    #data=struct.pack("!i",pad)
    #tosend=tosend+data #pad...
                
    messagetype=70
    data=struct.pack("!i",messagetype)
    tosend=tosend+data
                
    version=9
    data=struct.pack("!i",version)
    tosend=tosend+data
                
    
    data=struct.pack("!i",ctrlid)
    tosend=tosend+data

    data=struct.pack("<f",value)
    tosend=tosend+data #pad...
                                 
    connection.sendall(tosend)

def senderror(flag,connection):  # flag = char 0 or 1
    header=b'ACATMSG'
    data=struct.pack("<8s",header)

    tosend=data

    lendata=21
    data=struct.pack("!i",lendata)
    tosend=tosend+data
                
    #pad=0
    #data=struct.pack("!i",pad)
    #tosend=tosend+data #pad...
                
    messagetype=200
    data=struct.pack("!i",messagetype)
    tosend=tosend+data
                
    version=9
    data=struct.pack("!i",version)
    tosend=tosend+data
                
    
    data=struct.pack("<c",flag)
    tosend=tosend+data

    connection.sendall(tosend)

def recverror(data): # messagte type = 200 from CONTAMX

  # not consistent with doucmentation that states that it should be a char, but it looks like int....
    flag=struct.unpack("!i",data[0:4])[0]
    if (flag==1):
        print ("Normal CONTAMX end")
    if (flag==0):
        print ("CONTAMX terminated with error, check log")






def readwth(filename):
    #making assumption there are 8760 values, i.e. 1 per hour
    
    f=np.loadtxt(filename,skiprows=371,usecols=(2,3,4,5))

    T=f[:,0]
    p=f[:,1]
    Ws=f[:,2]
    Wd=f[:,3]

    return T,p,Ws,Wd


def setwth(abstime,startday,T,p,Ws,Wd,connection):

    #abstime = simulation time in s from 00:00 of start day
    #fromJan01Time = time from 1 jan (refrence for weather)

    fromJan01Time=(abstime+(startday-1)*24*3600)/3600. # time in h from jan01
    
    i=int(np.floor(fromJan01Time))

        
    wiplus1=fromJan01Time-i
    wi=1-wiplus1

    #print (abstime,startday,i)
    
    # c suffix = 'current'
    if (i<8760):
        Tc=T[i]*wi+T[i+1]*wiplus1
        pc=p[i]*wi+p[i+1]*wiplus1
        Wsc=Ws[i]*wi+Ws[i+1]*wiplus1
        Wdc=Wd[i]*wi+Wd[i+1]*wiplus1
    else:
        Tc=T[i-8760]*wi+T[i-8760+1]*wiplus1
        pc=p[i-8760]*wi+p[i-8760+1]*wiplus1
        Wsc=Ws[i-8760]*wi+Ws[i-8760+1]*wiplus1
        Wdc=Wd[i-8760]*wi+Wd[i-8760+1]*wiplus1

   
    header=b'ACATMSG'
    data=struct.pack("<8s",header)

    tosend=data

    lendata=36
    data=struct.pack("!i",lendata)
    tosend=tosend+data
                
    #pad=0
    #data=struct.pack("!i",pad)
    #tosend=tosend+data #pad...
                
    messagetype=80
    data=struct.pack("!i",messagetype)
    tosend=tosend+data
                
    version=9
    data=struct.pack("!i",version)
    tosend=tosend+data
                
    # order: temp, p, Ws, Wd
    data=struct.pack("<f",Tc)
    tosend=tosend+data 
    data=struct.pack("<f",pc)
    tosend=tosend+data 
    data=struct.pack("<f",Wsc)
    tosend=tosend+data 
    data=struct.pack("<f",Wdc)
    tosend=tosend+data 
                                 
    connection.sendall(tosend)

    return(Tc,Wsc)


def main(port,weatherFile,updatecontrolsFunction):

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', port)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)
        
            
    firstPass=True         # boolean to chek first pass in UPDATE CONTROLS

    printfrequency=86400 # 86400 seconds


    allconcentrations=[]
    oldvalues=[]

    #weatherfile='UCLmod.wth'

    Tw,pw,Wsw,Wdw=readwth(weatherFile)



    while True:
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print('connection from', client_address)

            while(True):
                
                s,data=readheader(connection)

                if (s==2): # generic information
                    dt,maxtime,startday=readtimeinfo(data)

                if (s==3):
                    contaminants=readcontaminants(data)
                    
                if (s==5): # read controls fr

                    ctrlid,ctrlnames,ctrlinitvals=readcontrols(data)

                if (s==8): #zone info

                    znames=readzones(data)


                if (s==120): # recieve contaminants (!! Written 100 in documentation but wrong)

                    
                    
                    contaminantid,zonesconcentration=recv1contaminant(data,len(znames))
                    allconcentrations.append(zonesconcentration)
     
                    specie=contaminants[contaminantid-1] # ids start at 1 in contam, while arrays are indexed from 0 in python
                    #print ("Specie ",specie)
                    #print ("Recieve contaminant data")
                    
                    
                    
                if (s==200): # error message
                    recverror(data)
                    connection.close()
                    exit()

                    
                if (s==0): # contam ready to wait informations

                    #0 get current time (in s)
                    currenttime=contamready(data)
                    
                    #first pass -> set initial abstime
                    if (firstPass==True):
                        abstime=currenttime
                    else:
                        abstime+=dt


                    if (currenttime==86400):
                        
                        print("Day ",abstime/86400)
                    

                    #1a - Update weather
                    Tnow,Wsnow=setwth(abstime,startday,Tw,pw,Wsw,Wdw,connection)
                    
                        
                    
                    #1b - UPDATE controls

                    #controls,values,oldvalues=updatecontrols(ctrlnames,ctrlinitvals,contaminants,znames,allconcentrations,oldvalues,abstime,dt,firstPass,[Tnow,Wsnow],controls=controlslist,parameters=parameters)
                    controls,values,oldvalues=updatecontrolsFunction(ctrlnames,ctrlinitvals,contaminants,znames,allconcentrations,oldvalues,abstime,dt,firstPass,[Tnow,Wsnow])

                    
                    for control in controls: #controls = list to modify, ctrlnames = list of controls in CONTAM

                        myindex=controls.index(control) # myindex = index is the result list above
                        value=values[myindex]
                       
                        contamindex=ctrlnames.index(control) # hypothesis : apparence order in the CONTAM index
                        
                        writecontrol(contamindex+1,value,connection) # !!!see my comment about index and CID in function "writecontrol"


                        
                    #2 purge old data

                    #print ("Purging data")
                    allconcentrations=[]

                        
                    #3 - tell contam to continue to next time step

                    if(dt<120):
                        dt=120

                    firstPass=False
                    advance(2,abstime+dt,connection) # option 2: update concentrations
                    

                    
                    if(currenttime>=maxtime):
                        senderror('1')
                        input('waiting contam to finish')
                        
        finally:
            # Clean up the connection
            connection.close()



if __name__ == '__main__':

    
    port = 8200
    import generic_controller 
    main(port,'UCLmod.wth',generic_controller.updatecontrols)