#usable

#skript to start OLEDPOWER for different cavity-thicknesses for polarisation_fitting
# output is K_all

from pylab import*
import os as os
import scipy as sp
import time as time
import sys as sys
import matplotlib.pyplot as plt
import numpy as np
import ReaderVariations as reader



# enter parameters

k_min=0
k_max=3.5
k_steps=0.002
wave_min=451
wave_max=700
wave_steps=1
angle_min=0
angle_max=89
angle_steps=1

thickness_min=100
thickness_max=150
thickness_count=3

# make folder where the simulation will be stored
os.mkdir('cavities')

# create a new parameter file
f=open('InputFiles/parameters.txt', 'w')
f.seek(0)

string='$' + '\t' + '\t' + 'wavelength' +' ' + str(wave_min) + ' ' + str(wave_max) + ' ' + str(wave_steps) + '\n'
string+='$' + '\t' + '\t' + 'k_parallel' + ' ' + str(k_min) + ' ' + str(k_max) + ' ' + str(k_steps)

f.write(string)
f.close()



# create a class for an OLED layer
class OledLayer:
    "an OLED layer with position and type"
    position_ = 0
    thickness_ = 0
    material_ = 'unknown'
    type_ = 'unknown'
    
    def __init__(self,num1,num2,string1,string2):
        self.position_ = num1
        self.thickness_ = num2
        self.material_ = string1
        self.type_ = string2

# create a class for the thickness variation        
class Variation:
    "parameter variation"
    position_ = 0
    values_ = () # create a tuple
    
    def __init__(self,num1,list1):
        self.position_ = num1
        self.values_ = list1
        
values1 = []


# all of this is in the main python script (important if different instances are called, probably not crucial here)
if __name__ == "__main__":

    # define name of the executable for the OLEDPOWER simulation with "k"
    exeFile = "main_k.exe"
    
    # define spectra which is used
    PLfile = 'PLSpectrum_CBPIrppy2acac_0'
    
    # define Layer stack for simulation
    # this can be changed to "TOP" for a top emitting OLED, not sure if one has still to invert the stack, but one could find this out by doing clever simulations
    simulation = 'BOTTOM'
    # create a list of layers
    Oled = []
    # append different Layers as defined earlier in the Layer Class, thickness is in nanometer, Layer with PL spectrum has to be non absorbing --> note the different kind of layers: semi, substrate, passive, active
    Oled.append( OledLayer(0,1.,'AIR','semi'))
    Oled.append( OledLayer(1,1e6,'Glass','substrate'))
    Oled.append( OledLayer(2,90.,'ITO_IAPP','passive'))
    Oled.append( OledLayer(3,50.,'NHT5_NDP2','passive'))
    Oled.append( OledLayer(4,10.,'STAD_0','passive'))
    Oled.append( OledLayer(5,18.,'CBPIrppy2acac_0','active'))
    Oled.append( OledLayer(6,10.,'BAlq','passive'))
    Oled.append( OledLayer(7,20.,'BPhenCs_0','passive'))
    Oled.append( OledLayer(8,100.,'BPhenCs','passive'))
    Oled.append( OledLayer(9,100.,'Ag_FWiz','passive'))
    Oled.append( OledLayer(10,1.,'AIR','semi'))
    
    # set variation (only 1 variation is allowed here), Variation(position --> which layer should be varied, list of thicknesses) --> usually the ETL is varied
    # the "20" is introduced because there should no absorbing medium close to the active layer --> take a 20nm layer and add it, same "n" values but "k=0"
    var1 = Variation(8,sp.linspace(thickness_min-20,thickness_max-20,thickness_count))

    # update the thickness of the ETL (+20 nm) ## NOT NEEDED ANYMORE???
    #layerthickness = var1.values_ + Oled[var1.position_ - 1].thickness_
    
    # how many simulations will be done? Only important for printing
    nSimulations = len(var1.values_)
    # introduce a variable for counting which thickness is processed
    counter = 1
    
    ###########################################
    # Calculation over in-plane wave vector k #
    ###########################################

    # start loop over the different thickness values
    for i in range(len(var1.values_)):
        # make different lists to store the data
            k=[]    #angle
            ktmv=[]    
            ktmh=[]
            kteh=[]
            utmv=[]
            utmh=[]
            uteh=[]
            wav=[] #wave lengths
            waste=[]        
            ktmv_all=[]
            ktmh_all=[]
            kteh_all=[]
            utmv_all=[]
            utmh_all=[]
            uteh_all=[]            
            # print to the user what is calculated at the moment
            print '\nSimulation no. ', counter,'/',nSimulations, ':'
            print 'Layer no. ', var1.position_, ': thickness ',var1.values_[i]
            # update the thickness of the layer which is varied
            Oled[var1.position_].thickness_ = var1.values_[i]
            
            # open the "device" file where the OLED layer structure is written down
            f = open('InputFiles/device.txt', 'w')
            # write the layers into the file
            for i_layer in range(len(Oled)):
                f.write('$\t')
                f.write( Oled[i_layer].material_)
                f.write('\t')
                f.write(str( Oled[i_layer].thickness_))
                f.write('\t')
                f.write(Oled[i_layer].type_)
                
                if Oled[i_layer].type_ == 'active':
                    f.write('\t')
                    f.write(PLfile)
                    
                f.write('\n')
            
            f.write('\n')
            f.close()
            
            # I DONT KNOW WHY THIS IS IN HERE, seems to me as if this is not really needed
            f = open('InputFiles/device.txt', 'r')
            f.close()
            
            # wait for one second to make sure that the device file is written before it is read by OLEDPOWER    
            time.sleep(1)
            # get the error message (which is usually no error) from OLEDPOWER
            simulationOK = os.system(exeFile)
            
            # if the simulation went well (error code "0" is given)
            if (simulationOK==0):
                # only for bottom stacks
                if (simulation == 'BOTTOM'):

                    # open the PowerSpectra file to read WHAT?
                    p = open('SimulationResults/PowerSpectra.txt', 'r')
                    # go to the beginning of the file
                    p.seek(0)                        
                    # reads all data into one string
                    string = p.read()                    

                    # introduces Counter to distinguish between lines
                    lineCounter=0                
                    # splits data into lines         
                    for thisLine in string.split('\n'):
                        # for first line do the following, because the first line has a different structure          
                        if lineCounter == 0:
                            # sets position counter to zero                
                            positioncounter = 0                
                            # splits lines into columns
                            for x in thisLine.split(' '):
                                # if first position and there is something
                                if positioncounter == 0 and len(x)>0:                                     
                                    waste.append(x)            
                                # at first position do:    
                                if positioncounter == 1 and len(x)>0:    
                                    # append to waves list
                                    wav.append(float(x[4:]))        
                                # add one to the position
                                positioncounter +=1        
                        # for all other lines except the first
                        if lineCounter > 0:                
                            positioncounter = 0    
                            for x in thisLine.split(' '):
                                if positioncounter == 0 and len(x)>0: 
                                    try:            
                                        # check if string is a float number
                                        float(x)    
                                        # if yes, append to k list
                                        k.append(float(x)) 
                                    except:    
                                        wav.append(float(x[4:])) # if no float, append to waves list the part which is float
                                # the next 6 "if"s will read the K (power inside cavity) and U (outcoupled power) into lists. The values will be "back-corrected" as they were weighted with isotropic orientation
                                # equations 16 and 22 in M. Furnos Paper
                                if positioncounter == 1 and len(x)>0: 
                                    ktmv.append(float(x)*3)    
                                if positioncounter == 2 and len(x)>0:
                                    ktmh.append(float(x)*(float(3)/2))
                                if positioncounter == 3 and len(x)>0:
                                    kteh.append(float(x)*(float(3)/2))
                                if positioncounter == 7 and len(x)>0:
                                    utmv.append(float(x)*3)
                                if positioncounter == 8 and len(x)>0:
                                    utmh.append(float(x)*(float(3)/2))
                                if positioncounter == 9 and len(x)>0:
                                    uteh.append(float(x)*(float(3)/2))
                                positioncounter +=1
                        lineCounter += 1
                    # close file
                    p.close()

        
                    # calculate how many angle-steps (k-steps) are used
                    k_number=(float(k_max)-float(k_min))/float(k_steps)+1
                    k_number=int(k_number)

                    # integration of K over angle (this could probably done faster but is not the time limiting factor) --> this yields the Purcell-Factor F(lambda)
                
                    # loop over the blocks of each wavelength
                    for j in range(1, len(k)/k_number+1): 
                        ktmv_a=0
                        ktmh_a=0
                        kteh_a=0
                        # integration over every angle
                        for o in range(k_number*(j-1), k_number*j-1):    
                            # trapeze-integration for every part of K
                            ktmv_a+=(k[o+1]-k[o])/2.0*(ktmv[o]+ktmv[o+1]) 
                            ktmh_a+=(k[o+1]-k[o])/2.0*(ktmh[o]+ktmh[o+1]) 
                            kteh_a+=(k[o+1]-k[o])/2.0*(kteh[o]+kteh[o+1]) 
                        # writes values into lists
                        ktmv_all.append(ktmv_a)        
                        ktmh_all.append(ktmh_a)
                        kteh_all.append(kteh_a)    

                    # integration of U over angle
                    # counts how many wavelengths are investigated
                    for j in range(1, len(k)/k_number+1): 
                        utmv_a=0
                        utmh_a=0
                        uteh_a=0
                        # integration over every angle
                        for o in range(k_number*(j-1), k_number*j-1):    
                            # trapeze-integration for every part of U
                            utmv_a+=(k[o+1]-k[o])/2.0*(utmv[o]+utmv[o+1]) 
                            utmh_a+=(k[o+1]-k[o])/2.0*(utmh[o]+utmh[o+1]) 
                            uteh_a+=(k[o+1]-k[o])/2.0*(uteh[o]+uteh[o+1]) 
                        # writes values into lists
                        utmv_all.append(utmv_a)        
                        utmh_all.append(utmh_a)
                        uteh_all.append(uteh_a)

                    # temporal thickness variable
                    t = str(var1.values_[i]+20)
                    # make a folder in the cavities folder for the new thickness
                    os.mkdir('cavities/' + t[:(len(t)-2)])
                    # create a new file and write the F and U
                    K_all_file = open('cavities/' + t[:(len(t)-2)]+'/K_all.txt', 'w')

                    # write all the components into one line and then write the line
                    for l in arange(len(ktmv_all[:])):    
                        line = str(ktmv_all[l]) + '\t' +str(ktmh_all[l]) + '\t' +str(kteh_all[l]) + '\t'
                        line += str(utmv_all[l]) + '\t' +str(utmh_all[l]) + '\t' +str(uteh_all[l]) + '\n'
                        K_all_file.write(line)
                    K_all_file.close()    
            
            
                    # increase counter
                    counter += 1

    ################################
    # calculation over solid angle #
    ################################

    # I am not sure if this has to be done at all or if this can not be achieved by using U from the above simulation and convert it to solid angle --> this would save some computation time but might make things more difficult. --> how would one need to convert the in-plane wave vector to solid angle? Eq. A17 in M. Furnos Paper?


    f=open('InputFiles/parameters.txt', 'w')
    f.seek(0)

    string='$' + '\t' + '\t' + 'wavelength' + ' ' + str(wave_min) + ' ' + str(wave_max) + ' ' + str(wave_steps) + '\n'
    string+='$' + '\t' + '\t' + 'angle' + ' ' + str(angle_min) + ' ' + str(angle_max) + ' ' + str(angle_steps)

    f.write(string)
    f.close()    

         
    values1 = []

    waves = []

    # reset the counter
    counter = 1 

    # define name of the executable for the OLEDPOWER simulation with "angle"
    exeFile = "main_angle.exe"

    # start loop over the different thickness values
    for i in range(len(var1.values_)):

            # print to the user what is calculated at the moment
            print '\nSimulation no. ', counter,'/',nSimulations, ':'
            print 'Layer no. ', var1.position_, ': thickness ',var1.values_[i]
            # update the thickness of the layer which is varied
            Oled[var1.position_].thickness_ = var1.values_[i]

            # open the "device" file where the OLED layer structure is written down
            f = open('InputFiles/device.txt', 'w')
            # write the layers into the file
            for i_layer in range(len(Oled)):
                f.write('$\t')
                f.write( Oled[i_layer].material_)
                f.write('\t')
                f.write(str( Oled[i_layer].thickness_))
                f.write('\t')
                f.write(Oled[i_layer].type_)
                
                if Oled[i_layer].type_ == 'active':
                    f.write('\t')
                    f.write(PLfile)
                    
                f.write('\n')
            
            f.write('\n')
            f.close()
            
            # I DONT KNOW WHY THIS IS IN HERE, seems to me as if this is not really needed
            f = open('InputFiles/device.txt', 'r')
            f.close()
            
            # wait for one second to make sure that the device file is written before it is read by OLEDPOWER
            time.sleep(1)
            # get the error message (which is usually no error) from OLEDPOWER
            simulationOK = os.system(exeFile)

            # if the simulation went well (error code "0" is given)
            if (simulationOK==0):
                # only for bottom stacks
                if (simulation == 'BOTTOM'):
                    t=str(var1.values_[i]+20)
                        
                    # define function to load intensity data of one file, DOES IT HAVE TO BE HERE DEFINED IN THE LOOP? NOT PRETTY BUT IT WORKS
                    def intensity(data):
                        # read file 
                        f=open(data, 'r')

                        string = f.read()

                        angles=[]
                        waves=[]
                        intens=[]

                        # read angles, waves, intensities
                        linecounter=0
                        for thisline in string.split('\n'):
                            if linecounter ==0:
                                positioncounter=0
                                for x in thisline.split():
                                    if positioncounter >= 1:
                                        angles.append(x)
                                    positioncounter +=1
                            if linecounter >0:
                                positioncounter=0
                                for x in thisline.split():
                                    if positioncounter ==0:
                                        waves.append(int(x))
                                    if positioncounter >0:
                                        intens.append(x)
                                    positioncounter+=1
                            linecounter+=1





                        # create a list of wavelengths which is repetitive
                        wave=waves[0]
                        waves_full=[]
                        for i in range(len(waves[:])):
                            for j in range(len(angles[:])):
                                waves_full.append(wave)
                            # get wave step from the data itself, although it should be the same as given in the beginning
                            wave+=waves[1]-waves[0]


                        # create a list of angles which is repetitive
                        angles_full=[]
                        for j in range(len(waves[:])):
                            for i in range(len(angles[:])):
                                angles_full.append(angles[i])


                        # open the right thickness folder and write the file
                        f=open('cavities/' + t[:(len(t)-2)] + '/' +data[18:], 'w')    
                        string2=str()
                        for i in range(len(intens[:])):
                            string2+=str(angles_full[i]) +'\t' + str(waves_full[i])  +'\t' + str(intens[i]) + '\n'
                        f.write(string2)
                        f.close()

                    # read all three SpectralRadiantIntensity files and write them in the format we want
                    intensity('SimulationResults/SpectralRadiantIntensity_TMh.txt')
                    intensity('SimulationResults/SpectralRadiantIntensity_TEh.txt')
                    intensity('SimulationResults/SpectralRadiantIntensity_TMv.txt')            

                    counter += 1

    
    







