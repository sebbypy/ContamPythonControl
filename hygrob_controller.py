

#from pylab import *
from numpy import sum as npsum
from numpy import asarray as npasarray
from numpy import exp

# definition of global variables --> avoid them as much as possible

co2_kgkg2ppm=658008    # conversion from kg/kg CO2 to ppm
h2o_kgkg2RH=69.68*100  # convertosn to kg/kg H2O to RH in percent (for 20 deg)



def updatecontrols(controlslist,initvals,specieslist,zonelist,concentration_data,oldvalues,abstime,dt,firstPass,w,controls=[],parameters={}):

    
    # INPUTS
    
    # controlslist         List of all constant control varialbes existing in the CONTAM model
    # initvals             Initial values of all available controls
    # specieslist          List of species in the model
    # zonelis              List of zones in the model
    # cocentration_Data    concentration matrix of all species in all rooms at current time step
    # oldvalues            List of the selected control inputs at previous time step
    # W = weather          [Text, Wv]
    # controls             list of controls to be modified: this is optionnal. This allow either to give them in the main function, or either here
    # parameers            to give the possibility to send parameters from the main function as a dictionnary
    Text=w[0]
    Wvel=w[1]

    
    # OUTPUTS

    # controls             List of the CONTAM controls (by name) that will be set in this controller (--> other will remain unchanged in the model!)
    # values               Value of each of "controls" that will be send to contam
    # (old)values          Return values a second time, it will be sorted as oldvalues in main function
    

    # LIST OF CONTROLS THAT WE WANT TO DEFINE IN THIS FUNCTION

    controls=['C_RP_Wasplaats','C_RP_Keuken','C_RP_WC','C_RP_Badkamer','C_RP_Inkomhal','C_RTO_Slaap1','C_RTO_Slaap2','C_RTO_Slaap3','C_RTO_Woonkamer']
    
    
    # check that the demanded variables exist
    if (firstPass==True):
        print(controls)
        print(parameters)
        oldvalues=checkcontrols(controls,controlslist,initvals) #
       
            
    # BEGIN OF CONTROLLER

    values=[]

       
    #main parameters
    Qmin=0.1
    Qmax=1.0
    co2min=500
    co2max=1000
    RHmin=30
    RHmax=70


    #get H2O concentration in Various Rooms (in kg/kg) and converting it to RH
    RH_Keuken=getconcentration('H2O','Keuken',specieslist,zonelist,concentration_data)*h2o_kgkg2RH
    RH_Badkamer=getconcentration('H2O','Badkamer',specieslist,zonelist,concentration_data)*h2o_kgkg2RH
    RH_Wasplaats=getconcentration('H2O','Wasplaats',specieslist,zonelist,concentration_data)*h2o_kgkg2RH


    #Absolue humidity
    AH_Woonkamer=getconcentration('H2O','Woonkamer',specieslist,zonelist,concentration_data)
    AH_Slaap1=getconcentration('H2O','Slaapkamer_1',specieslist,zonelist,concentration_data)
    AH_Slaap2=getconcentration('H2O','Slaapkamer_2',specieslist,zonelist,concentration_data)
    AH_Slaap3=getconcentration('H2O','Slaapkamer_3',specieslist,zonelist,concentration_data)

    #Temperature "percieved" by the Hygro air inlet    
    TViewed=0.7*293.15+0.3*Text  # kelvin
    TViewed=TViewed-273.15
    
    #Conversion for AH to RH but at Tviewed (see functions at the end of the file)
    RH_Woonkamer=Moisture2RH(AH_Woonkamer,TViewed)
    RH_Slaap1=Moisture2RH(AH_Slaap1,TViewed)
    RH_Slaap2=Moisture2RH(AH_Slaap2,TViewed)
    RH_Slaap3=Moisture2RH(AH_Slaap3,TViewed)



    valsdict={}
    
    for control in controls:
        index=controls.index(control)
        
        if (control=='C_RTO_Woonkamer'):
            val=linear(RH_Woonkamer,1,43.8/5.7,51,65)
            
        elif (control=='C_RTO_Slaap1'):
            val=linear(RH_Slaap1,1,43.8/5.7,51,65)

        elif (control=='C_RTO_Slaap2'):
            val=linear(RH_Slaap2,1,43.8/5.7,51,65)

        elif (control=='C_RTO_Slaap3'):
            val=linear(RH_Slaap2,1,43.8/5.7,51,65)

        elif (control=='C_RP_Wasplaats'):
            val = linear(RH_Wasplaats,5,45,45,85)  #5m3/h at 45 pc RH     45 m3/h at 85% RH
            
        elif (control=='C_RP_Badkamer'):
            val = linear(RH_Badkamer,5,45,45,85)  #5m3/h at 45 pc RH     45 m3/h at 85% RH

    
        elif (control=='C_RP_Keuken'):

            val = linear(RH_Keuken,15,55,23,63)  #5m3/h at 45 pc RH     45 m3/h at 85% RH
        elif (control=='C_RP_Inkomhal'):
            val = 0

        elif (control=='C_RP_WC'):
            val = 1
        
        else:
            print ("error",control)
            return
        
                
        valsdict[control]=val


    #EN OF LOOP

    # END OF CONTROLLER

    #only returns the values in the list ; other remain unchanged
    
    controls=[]
    values=[]
    
    for c,val in valsdict.items():
        controls.append(c)
        values.append(val)

    if firstPass:
        print("Modified controls",controls)

        
    #checking the number of returned values is correct compared to the control lis
    if (len(values) != len(controls)):
        print ("Incorrect number of control values returned !!")
        exit()
            

        
    return controls,values,values




###### DEFINITION OF CONTROLLER FUNCTIONS (LINEAR, INTEGRAL, MOVING AVERAGE, ETC) ########
###### SHOULD NOT BE CHANGED


def linear(c,qmin,qmax,cmin,cmax):


    flin=((c-cmin)/(cmax-cmin))
    if flin<0:
        flin=0.
    if flin>1.0:
        flin=1.0
            
    f=qmin+flin*(qmax-qmin)
      
    return f



def onoff(c,cmin,cmax,oldvalue):


    if (c>cmax):
        return 1
    if (c<cmin):
        return 0

    else:
        return oldvalue
    



def balance(Qnsup,fsup,Qnret,fret):
    #balance supply and exhaust based on individual controls
    #expected as np arrays

    Qnsup=npasarray(Qnsup)
    fsup=npasarray(fsup)
    Qnret=npasarray(Qnret)
    fret=npasarray(fret)
    
    qtotsup=npsum(Qnsup*fsup)
    qtotret=npsum(Qnret*fret)

    ratio=qtotsup/qtotret

    if (ratio>1.0):
        fret=fret*ratio
    if (ratio<1.0):
        fsup=fsup/ratio

    return(fsup,fret)


def getconcentration(specie,zone,specieslist,zonelist,concentration_data):

    if (specie not in specieslist):
        print ("FATAL error: specie ",specie,"is not present in the CONTAM species list",specieslist)

    if (zone not in zonelist):
        print ("FATAL error: zone ",zone,"is not present in the CONTAM species list: ",zonelist)


        
    id1=specieslist.index(specie)
    id2=zonelist.index(zone)
        
    return(concentration_data[id1][id2])
    

       
def checkcontrols(controls,controlslist,initvals):
    
    oldvalues=[]
    
    for c in controls:
        if c not in controlslist:
            print ("FATAL error: control ",c,"is not present in the CONTAM control list",controlslist)
            input("Pres to quit ...")
            exit()


        index=controlslist.index(c)
        oldvalues.append(initvals[index])
        
    return oldvalues



def Moisture2RH(moist,T):
    #moisture in kg/kg
    #T in C
    patm=101325.
    MMratio=0.629
    
    pvap=moist*patm/(moist+MMratio)

    return (pvap/psat(T)*100)

def psat(T):
    #computes stauration pressure for given temperature (in C)
    #based on August-Roche-Magnus equation for Water Saturation Pressure

    psat=0.61094*exp((17.625*T)/(T+243.04))*1000 # in Pa

    return psat


