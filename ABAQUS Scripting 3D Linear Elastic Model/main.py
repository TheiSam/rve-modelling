#---Abaqus Python Scripting
#---Code to generate a 3D cubic RVE of a fibre-reinforced composite
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

#---Define cubic RVE size in micrometers
#---Bottom left corner of rectangle
op1=0
op2=0
#---Top right corner of rectangle
tp1= 105
tp2= tp1
#---Depth of cube
dep=tp1

#---Create Sketch and Part (CUBE)
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=10 * 200)
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(op1, op1), point2=(tp1, tp2))
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Part-11', type= DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Part-11'].BaseSolidExtrude(depth=dep, sketch=
    mdb.models['Model-1'].sketches['__profile__'])

#---import *.csv file with list of fibres (circles centre coordinates and radius)
import numpy as np
with open("C:/") as file_name: # INSERT FILE PATH HERE
    array = np.loadtxt(file_name, delimiter=",")
print(array)
data=array
print(len(data))

#---import *.csv file with list of voids (circles centre coordinates and radius)
with open("C:/") as file_name: # INSERT FILE NAME HERE
    array2 = np.loadtxt(file_name, delimiter=",")
print(array)
data2=array2
print(len(data))

#---Create Sketch and Part 2 (FIBRES)
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=10 * 200)
for n in data:
    mdb.models['Model-1'].sketches['__profile__'].CircleByCenterPerimeter(center=( n[0], n[1]), point1=(n[0], n[2] + n[1]))
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Part-22', type= DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Part-22'].BaseSolidExtrude(depth=dep, sketch=
    mdb.models['Model-1'].sketches['__profile__'])

#---Create Sketch and Part 3 (VOIDS)
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=10 * 200)
for n in data2:
    mdb.models['Model-1'].sketches['__profile__'].CircleByCenterPerimeter(center=( n[0], n[1]), point1=(n[0], n[2] + n[1]))
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Part-33', type= DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Part-33'].BaseSolidExtrude(depth=dep, sketch=
    mdb.models['Model-1'].sketches['__profile__'])


#---Create instances of fibres and cube and VOIDS parts in the assembly
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='Part-11-1', 
    part=mdb.models['Model-1'].parts['Part-11'])
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='Part-22-1', 
    part=mdb.models['Model-1'].parts['Part-22'])
#NEW
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='Part-33-1', 
    part=mdb.models['Model-1'].parts['Part-33'])

#---Create a new part by merging fibres and cube parts and keeping boundaries
mdb.models['Model-1'].rootAssembly.InstanceFromBooleanMerge(domain=GEOMETRY, 
    instances=(mdb.models['Model-1'].rootAssembly.instances['Part-11-1'], 
    mdb.models['Model-1'].rootAssembly.instances['Part-22-1']), 
    keepIntersections=ON, name='Part-44', originalInstances=SUPPRESS)

mdb.models['Model-1'].rootAssembly.InstanceFromBooleanCut(cuttingInstances=(
    mdb.models['Model-1'].rootAssembly.instances['Part-33-1'], ), 
    instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Part-44-1'], 
    name='Part-1', originalInstances=SUPPRESS)

#---Delete old parts and instances
del mdb.models['Model-1'].parts['Part-11']
del mdb.models['Model-1'].parts['Part-22']
del mdb.models['Model-1'].parts['Part-33']
del mdb.models['Model-1'].parts['Part-44']
del mdb.models['Model-1'].rootAssembly.features['Part-11-1']
del mdb.models['Model-1'].rootAssembly.features['Part-22-1']
del mdb.models['Model-1'].rootAssembly.features['Part-33-1']
del mdb.models['Model-1'].rootAssembly.features['Part-44-1']

#Translate and rotate part instance 
# so the center of the cube is in (0,0,0) and the fibres are aligned with the X-axis
mdb.models['Model-1'].rootAssembly.translate(instanceList=('Part-1-1', ), 
    vector=(-tp1/2, -tp1/2, -tp1/2))
mdb.models['Model-1'].rootAssembly.rotate(angle=90.0, axisDirection=(0.0, tp1/2, 
    0.0), axisPoint=(0.0, 0.0, 0.0), instanceList=('Part-1-1', ))

#Code to remove fibres that are outside the cube when that is the case

mdb.models['Model-1'].parts['Part-1'].DatumPlaneByPrincipalPlane(offset=0.0, 
    principalPlane=XYPLANE)
mdb.models['Model-1'].parts['Part-1'].DatumAxisByPrincipalAxis(principalAxis=
    YAXIS)
del mdb.models['Model-1'].sketches['__profile__']

mdb.models['Model-1'].ConstrainedSketch(gridSpacing=11.41, name='__profile__', 
    sheetSize=456.56, transform=
    mdb.models['Model-1'].parts['Part-1'].MakeSketchTransform(
    sketchPlane=mdb.models['Model-1'].parts['Part-1'].datums[2], 
    sketchPlaneSide=SIDE1, 
    sketchUpEdge=mdb.models['Model-1'].parts['Part-1'].datums[3], 
    sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
mdb.models['Model-1'].parts['Part-1'].projectReferencesOntoSketch(filter=
    COPLANAR_EDGES, sketch=mdb.models['Model-1'].sketches['__profile__'])
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0, 
    0), point2=(tp1, tp2))
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(-216.79, 
    -208.2325), point2=(216.79, 219.6425))
mdb.models['Model-1'].parts['Part-1'].CutExtrude(flipExtrudeDirection=ON, 
    sketch=mdb.models['Model-1'].sketches['__profile__'], sketchOrientation=
    RIGHT, sketchPlane=mdb.models['Model-1'].parts['Part-1'].datums[2], 
    sketchPlaneSide=SIDE1, sketchUpEdge=
    mdb.models['Model-1'].parts['Part-1'].datums[3])
del mdb.models['Model-1'].sketches['__profile__']


#Create materials properties for fibre and matrix
mdb.models['Model-1'].Material(name='Fibre')
mdb.models['Model-1'].materials['Fibre'].Density(table=((1.0, ), ))
mdb.models['Model-1'].materials['Fibre'].Elastic(table=((230, 0.2), 
    ))
#mdb.models['Model-1'].materials['Fibre'].Expansion(table=((-1e-06, ), ))
mdb.models['Model-1'].Material(name='Matrix')
mdb.models['Model-1'].materials['Matrix'].Density(table=((1e-07, ), ))
mdb.models['Model-1'].materials['Matrix'].Elastic(table=((9.5, 0.23), ))
#mdb.models['Model-1'].materials['Matrix'].Expansion(table=((8e-06, ), ))
mdb.models['Model-1'].HomogeneousSolidSection(material='Fibre', name=
    'Fibre', thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(material='Matrix', name=
    'Matrix', thickness=None)

#Create mesh
mdb.models['Model-1'].parts['Part-1'].seedPart(deviationFactor=0.1, 
    minSizeFactor=0.1, size=1.0)
mdb.models['Model-1'].parts['Part-1'].seedEdgeBySize(constraint=FINER, 
    deviationFactor=0.1, edges=
    mdb.models['Model-1'].parts['Part-1'].edges.findAt(((tp1, tp1, tp1/2), )), minSizeFactor=0.1, size=6.0)
mdb.models['Model-1'].parts['Part-1'].generateMesh()

#Assign material properties to matrix
mdb.models['Model-1'].parts['Part-1'].SectionAssignment(offset=0.0, 
    offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
    cells=mdb.models['Model-1'].parts['Part-1'].cells.findAt(((tp1, tp1, tp1/2),), )), sectionName='Matrix', thicknessAssignment=
    FROM_SECTION)

#Assign material properties to fibres
for n in data:
    mdb.models['Model-1'].parts['Part-1'].SectionAssignment(offset=0.0, 
    offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
    cells=mdb.models['Model-1'].parts['Part-1'].cells.findAt(((n[0], n[1], 0),), )), sectionName='Fibre', thicknessAssignment=
    FROM_SECTION)

#Regenerate assembly
mdb.models['Model-1'].rootAssembly.regenerate()
