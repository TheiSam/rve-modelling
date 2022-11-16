#####################################################
#IMPORT FILE
#Import file with Import keywords
#Import file with geometry, part, instance and mesh generation, and materials and section assigments, and STEP

# Run the parts_and_meshing.py file to create the part and meshing
execfile('C:/') # INSERT FILE PATH HERE


######################################################
#PERIODIC BOUNDARY CONDITIONS (PBC) IN 2D GENERATION

#PARAMETERS
#CHECK THEY ARE THE SAME DIMENSIONS AS THE IMPORTED GEOMETRY
#---Define cubic RVE size in micrometers (L = 1) or millimeters (L = 1000)
L = 1000.0
#---Bottom left corner of rectangle
op1=0
op2=0
#---Top right corner of rectangle
Wcomp= 105/L
Hcomp= Wcomp

Node_Tol = 0.001
#########################################

#Variables

#Instances
p = a.instances['Part-1-1']

#Edges
e = a.instances['Part-1-1'].edges
#######################################


EdgeUp=e.getByBoundingBox(0.0, Hcomp, 0.0, Hcomp, Hcomp, 0.0)
EdgeDo=e.getByBoundingBox(0.0, 0, 0.0, Hcomp, 0, 0.0)
EdgeRi=e.getByBoundingBox(Hcomp, 0, 0.0, Hcomp, Hcomp, 0.0)
EdgeLe=e.getByBoundingBox(0.0, 0, 0.0, 0, Hcomp, 0.0)

q1 = EdgeUp.index
q2 = EdgeDo.index
q3 = EdgeRi.index
q4 = EdgeLe.index

EdUp = EdgeUp
print('EdUp', len(EdUp))
EdDo = EdgeDo
EdRi = EdgeRi
EdLe = EdgeLe

a.Set(edges=EdUp, name='Up')
a.Set(edges=EdDo, name='Down')
a.Set(edges=EdRi, name='Right')
a.Set(edges=EdLe, name='Left')

# Finding the faces in the matrix
# Storing the nodes of faces
Upnodes = a.sets['Up'].nodes
Downnodes = a.sets['Down'].nodes
Rightnodes = a.sets['Right'].nodes
Leftnodes = a.sets['Left'].nodes

print('Upnodes', len(Upnodes))
print('Downnodes', len(Downnodes))
print('Rightnodes', len(Rightnodes))
print('Leftnodes', len(Leftnodes))

# Storing the coordinates and label of face nodes
UpCoord = []
DownCoord =[]
RightCoord = []
LeftCoord = []

for node in Upnodes:
    UpCoord = UpCoord + [[node.coordinates[0],node.coordinates[1],node.label]]
    
for node in Downnodes:
    DownCoord = DownCoord + [[node.coordinates[0],node.coordinates[1],node.label]]

for node in Rightnodes:
    RightCoord = RightCoord + [[node.coordinates[0],node.coordinates[1],node.label]]

for node in Leftnodes:
    LeftCoord = LeftCoord + [[node.coordinates[0],node.coordinates[1],node.label]]

UpCoord.sort(key=lambda coord: coord[0])
DownCoord.sort(key=lambda coord: coord[0])
RightCoord.sort(key=lambda coord: coord[1])
LeftCoord.sort(key=lambda coord: coord[1])

# Define Sets for Up and Bottom Faces
NumUp = len(UpCoord)
for i in range(0,NumUp):
    NLable = DownCoord[i][2]
    a.Set(nodes=p.nodes[NLable-1:NLable], name='DownNode_'+str(i))
    NLable = UpCoord[i][2]
    a.Set(nodes=p.nodes[NLable-1:NLable], name='UpNode_'+str(i))

NumRi = len(RightCoord)
for i in range(0,NumRi):
    NLable = RightCoord[i][2]
    a.Set(nodes=p.nodes[NLable-1:NLable], name='RightNode_'+str(i))
    NLable = LeftCoord[i][2]
    a.Set(nodes=p.nodes[NLable-1:NLable], name='LeftNode_'+str(i))

print('Numup', NumUp)
print('Numri', NumRi)


# Defining Constraints
# Up and Down
for i in range(1,NumUp-1):
    mdb.models['Model-1'].Equation(name='Const-UpDown-y'+str(i), terms=((-1.0, 'DownNode_'+str(i),2), (1.0, 'UpNode_'+str(i),2), (-1.0,'UpNode_0', 2)))

for i in range(1,NumUp-1):
    mdb.models['Model-1'].Equation(name='Const-UpDown-x'+str(i), terms=((1.0, 'DownNode_'+str(i),1), (-1.0, 'UpNode_'+str(i),1)))


# Right and Left
for i in range(1,NumRi-1):
    mdb.models['Model-1'].Equation(name='Const-LeRi-x'+str(i), terms=((-1.0, 'LeftNode_'+str(i),1), (1.0, 'RightNode_'+str(i),1), (-1.0,'RightNode_0', 1)))

for i in range(1,NumRi-1):
    mdb.models['Model-1'].Equation(name='Const-LeRi-y'+str(i), terms=((1.0, 'LeftNode_'+str(i),2), (-1.0, 'RightNode_'+str(i),2)))




#CONSTRAINTS CORNERS: i is from previous Up and DOWN
mdb.models['Model-1'].Equation(name='Con-TopCorners-y-R'+str(i+1)+'-L'+str(i+1), terms=((1.0, 
     'RightNode_'+str(i+1), 2), (-1.0, 'LeftNode_'+str(i+1), 2)))

mdb.models['Model-1'].Equation(name='Con-RightCorners-x-R'+str(i+1)+'-R0', terms=((1.0, 
     'RightNode_'+str(i+1), 1), (-1.0, 'RightNode_0', 1)))



# Load
# Fix left bottom corner along x and y directions
a = mdb.models['Model-1'].rootAssembly
v = a.instances['Part-1-1'].vertices
ver = v.findAt((0.0,0.0,0.0))
q = ver.index
Fixver = v[q:q+1]
region = a.Set(vertices=Fixver, name='Set-Fix')
mdb.models['Model-1'].PinnedBC(name='Fix', createStepName='Initial', region=region, localCsys=None)

# Fix left up corner along x direction
ver = v.findAt((0.0,Hcomp,0.0))
q = ver.index
Movever = v[q:q+1]
region = a.Set(vertices=Movever, name='LeftX')
mdb.models['Model-1'].DisplacementBC(name='LeftX', createStepName='Step-1', region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

# Fix right bottom corner along y direction
ver = v.findAt((Wcomp,0.0,0.0))
q = ver.index
Movever = v[q:q+1]
region = a.Set(vertices=Movever, name='Set-Move')
mdb.models['Model-1'].DisplacementBC(name='Set-Move', createStepName='Step-1', region=region, u1=4*0.01*Wcomp/2.0, u2=0.0, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
mdb.models['Model-1'].TabularAmplitude(data=((0.0, 0.0), (1.0, 1.0)), name=
    'Amp-1', smooth=SOLVER_DEFAULT, timeSpan=STEP)
mdb.models['Model-1'].boundaryConditions['Set-Move'].setValues(amplitude=
    'Amp-1')

mdb.models['Model-1'].rootAssembly.Set(elements=
    mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].elements.
        getByBoundingBox(0.0,0.0,0.0,71/1000.0,71/1000.0,0.0), name='SET-ALL')

# Job
mdb.Job(name='RVExTension', model='Model-1', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT,
    numCpus=1, numGPUs=0)
mdb.jobs['RVExTension'].setValues(activateLoadBalancing=False, numCpus=4, 
    numDomains=4)

