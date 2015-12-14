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

dicke_min=100
dicke_max=150
dicke_anzahl=51


os.mkdir('cavities')

f=open('InputFiles/parameters.txt', 'w')
f.seek(0)

string='$' + '\t' + '\t' + 'wavelength' +' ' + str(wave_min) + ' ' + str(wave_max) + ' ' + str(wave_steps) + '\n'
string+='$' + '\t' + '\t' + 'k_parallel' + ' ' + str(k_min) + ' ' + str(k_max) + ' ' + str(k_steps)

f.write(string)
f.close()




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
		
class Variation:
	"parameter variation"
	position_ = 0
	values_ = ()
	
	def __init__(self,num1,list1):
		self.position_ = num1
		self.values_ = list1
		
values1 = []



if __name__ == "__main__":

	exeFile = "main_k.exe"
	
	PLfile = 'PLSpectrum_CBPIrppy2acac_0'
	
	# Green Bottom Emitting OLED 2x emitter
	simulation = 'BOTTOM'
	Oled = []
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
	
	# set variation (only 1 variation is allowed here)
	var1 = Variation(8,sp.linspace(dicke_min-20,dicke_max-20,dicke_anzahl))

	# update the thickness of the ETL (+20 nm)
	layerthickness = var1.values_ + Oled[var1.position_ - 1].thickness_
	
	nSimulations = len(var1.values_)
	counter = 1
	
	for i in range(len(var1.values_)):
			k=[]	#angle
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
			print '\nSimulation no. ', counter,'/',nSimulations, ':'
			print 'Layer no. ', var1.position_, ': thickness ',var1.values_[i]
			Oled[var1.position_].thickness_ = var1.values_[i]
			
			f = open('InputFiles/device.txt', 'w')
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
			f.close
			
			f = open('InputFiles/device.txt', 'r')
			f.close
				
			time.sleep(1)
			simulationOK = os.system(exeFile)
			
			if (simulationOK==0):
				if (simulation == 'BOTTOM'):
					

				
			

					p = open('SimulationResults/PowerSpectra.txt', 'r')

					p.seek(0)						#go to the beginning of the file

					string = p.read()					#reads all data into one string

					lineCounter=0 						#introduces Counter to distinguishe between lines
					for thisLine in string.split('\n'): 			#splits data into lines
						if lineCounter == 0:				#for first line do the following
							positioncounter = 0			#sets position counter to zero	
							for x in thisLine.split(' '):
								if positioncounter == 0 and len(x)>0: #if first position and ther is something
									waste.append(x)				#splits lines into columns
								if positioncounter == 1 and len(x)>0:	#at first postion do:
									wav.append(float(x[4:]))		#append to waves list
								positioncounter +=1		#ad one to the position
						if lineCounter > 0:				#for all other lines than the first
							positioncounter = 0	
							for x in thisLine.split(' '):
								if positioncounter == 0 and len(x)>0: 
									try:			
										float(x)	#check if string is a float number	
										k.append(float(x)) #if yes, append to k list
									except:	
										wav.append(float(x[4:])) #if no float, append to waves list the part which is float
								if positioncounter == 1 and len(x)>0:	
									ktmv.append(float(x)*3)	#back-correction of the values of the K -parts --> results in the real numbers without weighting of dipole orientation, multiplication with factors given by user	
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
							 
					p.close()

		
					#calculate how many angle-steps are used
					k_number=float(k_max)/float(k_steps)+1
					k_number=float(k_number)

					#integration of K over angle
				
					for j in range(1, len(k)/k_number+1): #counts how many wavelenghts are investigatet
						ktmv_aa=0
						ktmh_aa=0
						kteh_aa=0
						for o in range(k_number*(j-1), k_number*j-1):	#integration over every angel
							ktmv_a=(k[o+1]-k[o])/2.0*(ktmv[o]+ktmv[o+1]) #trapezeintegration for every part of K
							ktmv_aa=ktmv_aa+ktmv_a
							ktmh_a=(k[o+1]-k[o])/2.0*(ktmh[o]+ktmh[o+1]) 
							ktmh_aa=ktmh_aa+ktmh_a
							kteh_a=(k[o+1]-k[o])/2.0*(kteh[o]+kteh[o+1]) 
							kteh_aa=kteh_aa+kteh_a
						ktmv_all.append(ktmv_aa)		#writes values into lists
						ktmh_all.append(ktmh_aa)
						kteh_all.append(kteh_aa)	

					#integration of U over angle
					for j in range(1, len(k)/k_number+1): #counts how many wavelenghts are investigatet
						utmv_aa=0
						utmh_aa=0
						uteh_aa=0
						for o in range(k_number*(j-1), k_number*j-1):	#integration over every angel
							utmv_a=(k[o+1]-k[o])/2.0*(utmv[o]+utmv[o+1]) #trapezeintegration for every part of U
							utmv_aa=utmv_aa+utmv_a
							utmh_a=(k[o+1]-k[o])/2.0*(utmh[o]+utmh[o+1]) 
							utmh_aa=utmh_aa+utmh_a
							uteh_a=(k[o+1]-k[o])/2.0*(uteh[o]+uteh[o+1]) 
							uteh_aa=uteh_aa+uteh_a
						utmv_all.append(utmv_aa)		#writes values into lists
						utmh_all.append(utmh_aa)
						uteh_all.append(uteh_aa)

						
					t=str(var1.values_[i]+20)
					os.mkdir('cavities/' + t[:(len(t)-2)])
					K_all_file = open('cavities/' + t[:(len(t)-2)]+'/K_all.txt', 'w')

					for l in arange(len(ktmv_all[:])):	
						zeile = str(ktmv_all[l]) + '\t' +str(ktmh_all[l]) + '\t' +str(kteh_all[l]) + '\t'
						zeile += str(utmv_all[l]) + '\t' +str(utmh_all[l]) + '\t' +str(uteh_all[l]) + '\n'
						K_all_file.write(zeile)
					K_all_file.close()	
			
			
			
					counter += 1

# get spectral data



f=open('InputFiles/parameters.txt', 'w')
f.seek(0)

string='$' + '\t' + '\t' + 'wavelength' + ' ' + str(wave_min) + ' ' + str(wave_max) + ' ' + str(wave_steps) + '\n'
string+='$' + '\t' + '\t' + 'angle' + ' ' + str(angle_min) + ' ' + str(angle_max) + ' ' + str(angle_steps)

f.write(string)
f.close()	


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
		
class Variation:
	"parameter variation"
	position_ = 0
	values_ = ()
	
	def __init__(self,num1,list1):
		self.position_ = num1
		self.values_ = list1
		
values1 = []

waves = []




if __name__ == "__main__":

	exeFile = "main_angle.exe"
	
	PLfile = 'PLSpectrum_CBPIrppy2acac_0'
	
	# Green Bottom Emitting OLED 2x emitter
	simulation = 'BOTTOM'
	Oled = []
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
	
	# set variation (only 1 variation is allowed here)
	var1 = Variation(8,sp.linspace(dicke_min-20,dicke_max-20,dicke_anzahl))

	# update the thickness of the ETL (+20 nm)
	layerthickness = var1.values_ + Oled[var1.position_ - 1].thickness_
	
	nSimulations = len(var1.values_)
	counter = 1
	
	for i in range(len(var1.values_)):
					
			print '\nSimulation no. ', counter,'/',nSimulations, ':'
			print 'Layer no. ', var1.position_, ': thickness ',var1.values_[i]
			Oled[var1.position_].thickness_ = var1.values_[i]
			
			f = open('InputFiles/device.txt', 'w')
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
			f.close
			
			f = open('InputFiles/device.txt', 'r')
			f.close
				
			time.sleep(1)
			simulationOK = os.system(exeFile)
			
			if (simulationOK==0):
				if (simulation == 'BOTTOM'):
					t=str(var1.values_[i]+20)
						
			
					def intensity(data):
						f=open(data, 'r')

						string = f.read()

						angles=[]
						waves=[]
						intens=[]

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






						wave=waves[0]
						waves_full=[]
						for i in range(len(waves[:])):
							for j in range(len(angles[:])):
								waves_full.append(wave)
							wave+=waves[1]-waves[0]


						angles_full=[]
						for j in range(len(waves[:])):
							for i in range(len(angles[:])):
								angles_full.append(angles[i])


	
						f=open('cavities/' + t[:(len(t)-2)] + '/' +data[18:], 'w')	
						string2=str()
						for i in range(len(intens[:])):
							string2+=str(angles_full[i]) +'\t' + str(waves_full[i])  +'\t' + str(intens[i]) + '\n'
						f.write(string2)
						f.close()

					intensity('SimulationResults/SpectralRadiantIntensity_TMh.txt')
					intensity('SimulationResults/SpectralRadiantIntensity_TEh.txt')
					intensity('SimulationResults/SpectralRadiantIntensity_TMv.txt')			

					counter += 1

	
	







