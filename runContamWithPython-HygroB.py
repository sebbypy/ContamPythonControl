import numpy as np
from server_test import getPort
import subprocess
import os
import server_windows
import time

import multiprocessing
#import generic_controller

inputPrjfile = 'HYGROB.prj'
weatherFile = "TestWeather.wth"
from hygrob_controller import updatecontrols



if __name__ == '__main__':

    print ("Running contam coupled with Python")
    
    
    # Searching for available port for socket connection
    port = getPort()
    
    # Launching Python server process
    p = multiprocessing.Process(target=server_windows.main,args=(port,weatherFile,updatecontrols))
    p.start()
    
    
    # Launching Contam Process
    contamExe = os.path.join('.','contamx3.exe')
    completedProcess=subprocess.run([contamExe,inputPrjfile,'-b','localhost:'+str(port),'-wp','-vf'],stderr=subprocess.PIPE)
           
    
    
    print("Contam Finished")
