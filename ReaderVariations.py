import numpy as np
from scipy import interpolate

def getSpectralData(fileU,fileF):

	waves = []
	variation = []
	U = []
	F = []
	
	# read variation, U, F
	f_U = open(fileU, 'r')
	print 'reading ', fileU
	
	f_U.seek(0)
	string = f_U.read()
	
	lineCounter = 0
	for thisLine in string.split('\n'):
		if (lineCounter==0):
			for word in thisLine.split('\t'):
				if len(word)>0 and word[0] != 'w':
					variation.append(float(word))
		else:
			positionCounter = 0
			if len(thisLine)>1:
				U.append([])
			for word in thisLine.split('\t'):
				if positionCounter == 0 and len(word)>0:
					waves.append(float(word))
				if positionCounter >0 and len(word)>0:
					U[len(U)-1].append(float(word))
				positionCounter +=1
		
		lineCounter += 1

	# read F
	f_F = open(fileF, 'r')
	print 'reading ', fileF
	
	f_F.seek(0)
	string = f_F.read()
	
	lineCounter = 0
	for thisLine in string.split('\n'):
		if (lineCounter==0):
			pass
		else:
			positionCounter = 0
			if len(thisLine)>1:
				F.append([])
			for word in thisLine.split('\t'):
				if positionCounter == 0 and len(word)>0:
					pass
				if positionCounter >0 and len(word)>0:
					F[len(F)-1].append(float(word))
				positionCounter +=1
		
		lineCounter += 1


	return (waves,variation,U,F)
	
def ReadPL(datafile,waves):
	print 'reading parameter file'
	#look up for how many waves the values are calculated
	f=open('InputFiles/parameters.txt', 'r')

	f.seek(0)

	string = f.read()
	
	f.close

	lineCounter=0
	for thisLine in string.split('\n'):
		if lineCounter ==0:
			positioncounter=0
			for x in thisLine.split():
				if positioncounter == 2:
					wave_min=int(x)
				if positioncounter == 3:
					wave_max=int(x)
				if positioncounter == 4:
					wave_step=int(x)
				positioncounter +=1
		lineCounter +=1

	waves_all=(wave_max-wave_min)/wave_step + 1

	waves=[]


	#list waves
	for i in range(0,waves_all):
		waves.append(float(wave_min+i*wave_step))

	print 'reading ', datafile
	waves_PL = []
	PLinput = []

	f = open(datafile, 'r')
	f.seek(0)

	string = f.read()

	lineCounter = 0
	for thisLine in string.split('\n'):
		if (len(thisLine) ==0) or (thisLine[0] == ' '):
			pass
		else:
			for word in thisLine.split(' '):
				if lineCounter == 0:
					waves_PL.append(float(word))
				else:
					PLinput.append(float(word))
		lineCounter += 1

	PLspectrum_photon_int = np.interp(waves,waves_PL,PLinput)
	
	hPlanck = 6.626068e-34 #m^2 kg / s
	cLight = 299792458 # m s^-1

	# devide with energy of every wavelength
	PL_photons1 = np.array(waves)*np.array(PLspectrum_photon_int)*1e-9 / (hPlanck*cLight)

	# calculate area of PL_photons1
	area = np.trapz(PL_photons1,waves)

	# normalize PL-photons1 -> PL_photons_normalized
	PL_normalized = PL_photons1 / area

	# calculate PL_energy
	PL_energy = PL_normalized / (np.array(waves) * 1e-9) * (hPlanck*cLight)

	return(PL_normalized)	

	
def ReadMeasuredEQE(datafile):

	print 'reading ', datafile
	
	current = 0
	EQE = []
	PE = []
	luminance = []
	#lumFlux = []
	ETLs = []
	V = []
	
	f = open(datafile, 'r')
	f.seek(0)
	string = f.read()
	
	for thisLine in string.split('\n'):
		if (len(thisLine) ==0) or (thisLine[0] == ' ') or (thisLine[0] == '#') \
					or (thisLine[0] == 'D'):
			pass
		else:
			positionCounter = 0
			for word in thisLine.split('\t'):
				if positionCounter ==4 and len(word)>0:
					current = float(word)
				if positionCounter ==1 and len(word)>0:
					ETLs.append(float(word))
				if positionCounter ==9 and len(word)>0:
					PE.append(float(word))
				if positionCounter ==10 and len(word)>0:
					EQE.append(float(word))
				if positionCounter ==2 and len(word)>0:
					V.append(float(word))
				if positionCounter ==5 and len(word)>0:
					luminance.append(float(word))
				positionCounter += 1
	
	current *= 1e-3*1e4	# conversion to A/m2
	
	#print EQE
	#print ETLs
	#print current
	return (current,ETLs,luminance,EQE,PE,V)
	
def ReadVLambda(wavesOut):

	datafile = 'VLambda.dat'
	print 'reading ', datafile
	
	x = []
	y = []
	
	f = open(datafile, 'r')
	f.seek(0)
	string = f.read()
	
	for thisLine in string.split('\n'):
		if (len(thisLine) ==0) or (thisLine[0] == ' '):
			pass
		else:
			positionCounter = 0
			for word in thisLine.split('\t'):
				if positionCounter==0 and len(word)>0:
					x.append(float(word))
				if positionCounter==1 and len(word)>0:
					y.append(float(word))
				positionCounter += 1
	
	VLambda = 683.002*np.interp(wavesOut,x,y)

	return VLambda
	
def getAffinity(fileA):

	waves = []
	variation = []
	aff = []
	
	# read variation, U, F
	f = open(fileA, 'r')
	print 'reading ', fileA
	
	f.seek(0)
	string = f.read()
	
	lineCounter = 0
	for thisLine in string.split('\n'):
		if (lineCounter==0):
			for word in thisLine.split('\t'):
				if len(word)>0 and word[0] != 'w':
					variation.append(float(word))
		else:
			positionCounter = 0
			if len(thisLine)>1:
				aff.append([])
			for word in thisLine.split('\t'):
				if positionCounter == 0 and len(word)>0:
					waves.append(float(word))
				if positionCounter >0 and len(word)>0:
					aff[len(aff)-1].append(float(word))
				positionCounter +=1
		
		lineCounter += 1

	return (waves,variation,aff)
	
def ReadPL2(datafile):
	
	print 'reading ', datafile
	waves = []
	PLinput = []
	
	f = open(datafile, 'r')
	f.seek(0)
	
	string = f.read()
	
	lineCounter = 0
	for thisLine in string.split('\n'):
		if (len(thisLine) ==0) or (thisLine[0] == ' '):
			pass
		else:
			for word in thisLine.split(' '):
				if lineCounter == 0:
					waves.append(float(word))
				else:
					PLinput.append(float(word))
		lineCounter += 1
		
	hPlanck = 6.626068e-34 #m^2 kg / s
	cLight = 299792458 # m s^-1
	PL_photons1 = np.array(waves)*np.array(PLinput)*1e-9 / (hPlanck*cLight)
	
	# calculate area of PL_photons1
	area = np.trapz(PL_photons1,waves)
	
	# normalize PL-photons1 -> PL_photons
	PL_normalized = PL_photons1 / area
	
	# calculate PL_energy
	PL_energy = PL_normalized / (np.array(waves) * 1e-9) * (hPlanck*cLight)
		
	return(waves,PL_normalized,PL_energy)
			
