# ContamPythonControl
Python scripts to interact with CONTAM simulations through socket connection


The purpose of this set of scripts is to be able to interact from Python with the CONTAM software at run time. This is done with the "CONTAMX TCP/IP SOCKET COMMUNICATION" feature described in the CONTAM 3.2 Appendix B. 


<h1>What can we do with that ? </h1>

Any "constant" control variable defined in CONTAM can be overwritten by any value through sockect communication. With this set of scripts, you can imagine any control logic you want for any of the controlled elements. 

<h1>What does it require ? </h1>
Only the scripts of this repository and the CONTAM executable (contamx.exe) in the same directory. All the scripts have been developped using CONTAM 3.2, and have not been tested yet with later versions. 


<h1>How do I execute it ? </h1>
The best way is to try with an example. They are two of them:
- a single zone model with one mechanical supply and one flow path to the exterior. The applied signal is a sine function. 
- a more complex model with more zones, more controls, which more or less reproduces the behavior of an French DCV system (hygro B), for which vents openings are dependent on the weather conditions


To run the examples, simply run:
python runContamWithPython-SingleZone.py
python runContamWithPython-HygroB.py


<h1>Questions and support</h1>
Don't hesitate to email me at sebastien.pecceu@bbri.be









