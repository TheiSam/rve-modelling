#Imports
from abaqus import *
from odbAccess import *
from abaqusConstants import *
from odbSection import *
import odb

#jobname='FILE NAME.odb' # ODB FILE NAME
#odb = session.openOdb(name=jobname)

# INSERT FILE PATHS HERE
odbPath = "C:/"  # INSERT FILE PATH TO OBD FILE GENERATED FROM RUNNING ABAQUS JOB
resultsGeneratedToPath = "C:/" # INSERT DESIRED PATH FOR STRESS STRAIN RESULTS CSV FILE TO BE GENERATED TO

#Odb file path
odb = openOdb(path=odbPath)


print("Reading E11 ODB FILE")
material = odb.rootAssembly.instances['PART-1-1'].sectionAssignments

num_of_mat=len(material)

domain=[]
for i in range(0,num_of_mat):
    domain.insert(i,material[i].region) # Select the Domain


frameRepository = odb.steps['Step-1'].frames
nframes=len(frameRepository);t11=[];
t11.insert(0,0) # t = 0
E11=[]
S11 = []
e11 = []

S11.append(0)
e11.append(0)

E11.insert(0,0) # t = 0
V12=[]
V12.insert(0,0) # t = 0
V13=[]
V13.insert(0,0) # t = 0
Frame_sig=[]; Frame_eps=[];Frame_ivol=[];
c=[]                           # volume fraction list stored (Order of information: Frame->material vol. fraction)
c.insert(0,[[0.0]]*num_of_mat)# Dummy zero volume at initial time
Eps11=[]                       # Total Strain  for 11-loading list stored (Order of information: Frame->Material->Components)
Sig11=[]                       # Stress tensor for 1-direction loading list stored (Order of information: Frame->Material->Components)
Eps11.insert(0,[[0.0]*6]*num_of_mat)
Sig11.insert(0,[[0.0]*6]*num_of_mat)
print("Reading Frames....")

for i in range(1,nframes): #Read each frame
    t11.insert(i, frameRepository[i].frameValue);
    Frame_ivol.insert(i-1,frameRepository[i].fieldOutputs['IVOL']) # Volume
    Frame_sig.insert(i-1,frameRepository[i].fieldOutputs['S']) # Stress
    Frame_eps.insert(i-1,frameRepository[i].fieldOutputs['LE'])# Strains
    Vol_mat_perframe = []
    E_mat_perframe = []
    Stress_mat_perframe = []
    for idx in range(0,num_of_mat): # Read each material section
        Vol=0
        Strain=0 #Initialization
        Stress=0 #Initialization
        IP=len(Frame_sig[i-1].getSubset(region=domain[idx],position=INTEGRATION_POINT).values) # Number of Integration Points
        ivol_domain=Frame_ivol[i-1].getSubset(region=domain[idx],position=INTEGRATION_POINT)
        sig_domain=Frame_sig[i-1].getSubset(region=domain[idx],position=INTEGRATION_POINT)
        eps_domain=Frame_eps[i-1].getSubset(region=domain[idx],position=INTEGRATION_POINT)
        for II in range(0,IP): #Read each INTEGRATION POINT
            Vol = Vol+ivol_domain.values[II].data
            Stress = Stress+sig_domain.values[II].data*ivol_domain.values[II].data
            Strain = Strain+eps_domain.values[II].data*ivol_domain.values[II].data 
        Vol_mat_perframe.insert(idx,Vol)
        Stress_mat_perframe.insert(idx,Stress)
        E_mat_perframe.insert(idx,Strain)
    Vol_frac=[]               #Volume fraction of phases in each frame
    Vol=sum(Vol_mat_perframe) # Total Volume
    Stress=0                  # Initialization 
    Strain=0                  # Initialization
    for idx in range(0,num_of_mat):
        Vol_frac.insert(idx,Vol_mat_perframe[idx]/Vol) #Volume fraction of phases in each frame
        Stress=Stress+ Stress_mat_perframe[idx] 
        Strain=Strain + E_mat_perframe[idx]
        Stress_mat_perframe[idx]=Stress_mat_perframe[idx]/(Vol*Vol_frac[idx]) #Average stress in material array per frame
        E_mat_perframe[idx]=E_mat_perframe[idx]/(Vol*Vol_frac[idx])           #Average strain in material array per frame
    c.append(Vol_frac)                # Volume fraction of different materials stored for all Frames
    Eps11.append(E_mat_perframe)      # Total strain in different materials stored for all Frames
    Sig11.append(Stress_mat_perframe) # Stress in different materials stored for all Frames 
    TOTALSig11 = sum(Sig11)/len(Sig11)
    Avg_Stress_11 = Stress/Vol #Effective Stress of Composite
    Avg_Strain_11 = Strain/Vol #Effective Strain of Composite
    stress1 = Avg_Stress_11[0] #Sigmaxx
    S11.append(stress1)
    strain1 = Avg_Strain_11[0] #Strainxx
    e11.append(strain1)
    strain2 = Avg_Strain_11[1] #Strainyy
    strain3 = Avg_Strain_11[2] #Strainzz
    E11.append((1e-9*stress1/strain1)) # Units in GPa
    V12.append(-strain2/strain1) # Effective Poissons Ratio
    V13.append(-strain3/strain1) # Effective Poissons Ratio

print('Avg_Stress_11', S11)
print('Avg_Strain_11', e11)
print('t11', t11)

import csv

# File path for the generated results to be written to
with open(resultsGeneratedToPath, "wb") as f: 
    writer = csv.writer(f, delimiter=',')
    writer.writerow(('Time', 'e11', 'S11'))
    for i in zip(t11, e11, S11):
        writer.writerow(i)

c[0]=Vol_frac; #Non-zero volume at initial time

