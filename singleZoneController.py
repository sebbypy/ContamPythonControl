

#from pylab import *
from numpy import sum as npsum
from numpy import asarray as npasarray
from numpy import exp
from numpy import sin

# definition of global variables --> avoid them as much as possible

co2_kgkg2ppm=658008    # conversion from kg/kg CO2 to ppm
h2o_kgkg2RH=69.68*100  # convertosn to kg/kg H2O to RH in percent (for 20 deg)



def updatecontrols(controlslist,initvals,specieslist,zonelist,concentration_data,oldvalues,abstime,dt,firstPass,w,controls=[],parameters={}):

    
    # INPUTS
    
    # controlslist         List of all constant control varialbes existing in the CONTAM model
    # initvals             Initial values of all available controls
    # specieslist          List of species in the model
    # zonelist              List of zones in the model
    # cocentration_Data    concentration matrix of all species in all rooms at current time step
    # oldvalues            List of the selected control inputs at previous time step
    # abstime               Absolute time in seconds
    # firstPass             boolean to tell if it is the 1st iteration or not
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

    controls=['TESTCONTROL']
    
    

       
            
    # BEGIN OF CONTROLLER

    valsdict = {}
    for controlName in controls:
    
        if (controlName == 'TESTCONTROL'):
            val = sin(abstime)
       
        
                
            valsdict[controlName]=val


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


