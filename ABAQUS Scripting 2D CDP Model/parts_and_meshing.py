#---Abaqus Python Scripting
#---Code to generate a 2D cubic RVE of a fibre-reinforced composite

#Imports needed to run the script via AbaqusCAE/File/Run Script 
from abaqus import *
from abaqusConstants import *
from caeModules import *

from abaqus import *
from abaqusConstants import *
from caeModules import *

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

#############################################
#DEFINE SIZE OF RVE
#Default units are microns:
#---Define cubic RVE size in micrometers (L = 1) or millimeters (L = 1000)
L = 1000.0
#---Bottom left corner of rectangle (origin point op (op1=0,op2=0))
op1=0
op2=0
#DEFINE SIZE OF CUBE(SQUARE IN 2D) BY DEFINING THE TOP CORNER
#---Top right corner of rectangle (top point tp (tp1,tp2) )
tp1= 70/L
tp2= tp1
#---Depth of cube for 3D models
dep= tp1

#Thickness of the cohesive element
th_coh = 0.1

###############################################
#IMPORT FIBRES AND VOIDS: GEOMETRICAL DATA 
import numpy as np

#FIBRES
#---import *.csv file with fibres coordinates (circles centre coordinates and radii) check if data is in microns or mm
with open("C:/") as file_name: # INSERT FILE PATH HERE
    array = np.loadtxt(file_name, delimiter=",")

#Convert data to mm
data_fibres=array/L



#VOIDS
#---import *.csv file with voids coordinates (circles centre coordinates and radii) check if data is in microns or mm
with open("C:/") as file_name: # INSERT FILE PATH HERE
    array2 = np.loadtxt(file_name, delimiter=",")

#Convert data to mm
data_voids=array2/L

###############################################
#IMPORT DATA FOR MATERIAL MODELS

#DATA FOR CONCRETE DAMAGE PLASTICITY (CDP) MODEL 

#COMPRESSIVE BEHAVIOR
#---import *.csv file with data for CDP model compressive yield stress vs inelastic strain
with open("C:/") as file_name: # INSERT FILE PATH HERE
    array4 = np.loadtxt(file_name, delimiter=",")
list_ystress_vs_inelastic_com = list(map(tuple, array4))

#COMPRESSIVE DAMAGE
#---import *.csv file with data for CDP model damage parameter compression vs inelastic strain
with open("C:/") as file_name: # INSERT FILE PATH HERE
    array5 = np.loadtxt(file_name, delimiter=",")
list_damage_vs_inelastic_com = list(map(tuple, array5))

#TENSILE BEHAVIOR
#---import *.csv file with data for CDP model tensile yield stress vs (cracking) inelastic strain
with open("C:/") as file_name: # INSERT FILE PATH HERE
    array6 = np.loadtxt(file_name, delimiter=",")
list_ystress_vs_inelastic_ten = list(map(tuple, array6))

#TENSILE DAMAGE
#---import *.csv file with data for CDP model damage parameter TENSILE vs inelastic strain (CRACKING)
with open("C:/") as file_name: # INSERT FILE PATH HERE
    array7 = np.loadtxt(file_name, delimiter=",")
list_damage_vs_inelastic_ten = list(map(tuple, array7))

##############################################################################
#Variables to simplify Abaqus python scripting

#Model
m = mdb.models['Model-1']

#Assembly
a = m.rootAssembly

#######################################
#CREATE PARTS AND INSTANCES

#CREATE PARTS

#CREATE PART CUBE 11
#---Create Sketch and Part 11 (CUBE) 2D deformable SHELL
m.ConstrainedSketch(name='__profile__', sheetSize=1 * 1)
m.sketches['__profile__'].rectangle(point1=(op1, op1), point2=(tp1, tp2))
m.Part(dimensionality=TWO_D_PLANAR, name='Part-11', type= DEFORMABLE_BODY)
m.parts['Part-11'].BaseShell(sketch=
    m.sketches['__profile__'])

#CREATE PART FIBRES 22
#---Create Sketch and Part 22 (FIBRES) 
# FIBRES FINAL RADIOUS IS THE FIBER RADIOUS MINUS THE THICKNESS OF THE COHESIVE ELEMENT (th_coh)
m.ConstrainedSketch(name='__profile__', sheetSize=10 * 200)
for n in data_fibres:
    m.sketches['__profile__'].CircleByCenterPerimeter(center=( n[0], n[1]), point1=(n[0], n[2] + n[1]-th_coh/L))
m.Part(dimensionality=TWO_D_PLANAR, name='Part-22', type= DEFORMABLE_BODY)
m.parts['Part-22'].BaseShell(sketch=
    m.sketches['__profile__'])

#CREATE PART INTERFACES 55
#---Create Sketch and Part 55 (INTERFACES)
m.ConstrainedSketch(name='__profile__', sheetSize=10 * 200)
for n in data_fibres:
    m.sketches['__profile__'].CircleByCenterPerimeter(center=( n[0], n[1]), point1=(n[0], n[2] + n[1]-th_coh/L))
    m.sketches['__profile__'].CircleByCenterPerimeter(center=( n[0], n[1]), point1=(n[0], n[2] + n[1]))
m.Part(dimensionality=TWO_D_PLANAR, name='Part-55', type= DEFORMABLE_BODY)
m.parts['Part-55'].BaseShell(sketch=
    m.sketches['__profile__'])

"""
#CREATE PART VOIDS 33
#---Create Sketch and Part 33 (VOIDS)
m.ConstrainedSketch(name='__profile__', sheetSize=1*1)
for n in data_voids:
    m.sketches['__profile__'].CircleByCenterPerimeter(center=( n[0], n[1]), point1=(n[0], n[2] + n[1]))
m.Part(dimensionality=TWO_D_PLANAR, name='Part-33', type= DEFORMABLE_BODY)
m.parts['Part-33'].BaseShell(sketch=
    m.sketches['__profile__'])
"""

#CREATE INSTANCES

#CREATE INTANCES CUBE, FIBRES, VOIDS, INTERACES
#---Create instances of fibres and cube and VOIDS AND INTERFACES parts in the assembly
a.DatumCsysByDefault(CARTESIAN)
a.Instance(dependent=ON, name='Part-11-1', 
    part=m.parts['Part-11'])
a.Instance(dependent=ON, name='Part-22-1', 
    part=m.parts['Part-22'])
#Voids instance:
#a.Instance(dependent=ON, name='Part-33-1', 
#    part=m.parts['Part-33'])
a.Instance(dependent=ON, name='Part-55-1', 
    part=m.parts['Part-55'])



#CREATE NEW PART INSTANCE THAT INCLUDES CUBE, FIBRES AND INTERFACES, AND VOIDS

#---Create a new part by merging fibres, interfaces and cube parts and keeping boundaries
a.InstanceFromBooleanMerge(domain=GEOMETRY, 
    instances=(a.instances['Part-11-1'], 
    a.instances['Part-22-1'],a.instances['Part-55-1'],), 
    keepIntersections=ON, name='Part-1', originalInstances=SUPPRESS)
    #keepIntersections=ON, name='Part-44', originalInstances=SUPPRESS)

"""
#---Create a new part from previous part-44 that includes the voids
a.InstanceFromBooleanCut(cuttingInstances=(
    a.instances['Part-33-1'], ), 
    instanceToBeCut=a.instances['Part-44-1'], 
    name='Part-1', originalInstances=SUPPRESS)
"""


#DELETE OLD PARTS AND INSTANCES

#---Delete old parts
del m.parts['Part-11']
del m.parts['Part-22']
#del m.parts['Part-33']
#del m.parts['Part-44']
del m.parts['Part-55']

#---Delete old instances
del a.features['Part-11-1']
del a.features['Part-22-1']
#del a.features['Part-33-1']
#del a.features['Part-44-1']
del a.features['Part-55-1']

#CODE TO REMOVE FIBRES OUTSIDE THE CUBE WHEN THAT IS THE CASE

m.parts['Part-1'].DatumPlaneByPrincipalPlane(offset=0.0, 
    principalPlane=XYPLANE)
m.parts['Part-1'].DatumAxisByPrincipalAxis(principalAxis=
    YAXIS)
del m.sketches['__profile__']

m.ConstrainedSketch(gridSpacing=11.41, name='__profile__', 
    sheetSize=456.56, transform=
    m.parts['Part-1'].MakeSketchTransform(
    sketchPlane=m.parts['Part-1'].datums[2], 
    sketchPlaneSide=SIDE1, 
    sketchUpEdge=m.parts['Part-1'].datums[3], 
    sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
m.parts['Part-1'].projectReferencesOntoSketch(filter=
    COPLANAR_EDGES, sketch=m.sketches['__profile__'])
m.sketches['__profile__'].rectangle(point1=(0, 
    0), point2=(tp1, tp2))
m.sketches['__profile__'].rectangle(point1=(-216.79, 
    -208.2325), point2=(216.79, 219.6425))
m.parts['Part-1'].CutExtrude(flipExtrudeDirection=ON, 
    sketch=m.sketches['__profile__'], sketchOrientation=
    RIGHT, sketchPlane=m.parts['Part-1'].datums[2], 
    sketchPlaneSide=SIDE1, sketchUpEdge=
    m.parts['Part-1'].datums[3])
del m.sketches['__profile__']

###################################################
#CREATE MATERIALS

#Create material properties for FIBRE
m.Material(name='Fibre')
#Density Uniform
m.materials['Fibre'].Density(table=((1.9E-9, ), ))
#Elastic Isotropic
m.materials['Fibre'].Elastic(table=((230000, 0.2), ))


#Create material properties for MATRIX
m.Material(name='Matrix')
#Density Uniform
m.materials['Matrix'].Density(table=((1.69e-09, ), ))

#Elastic Isotropic
m.materials['Matrix'].Elastic(table=((7700, 0.25), ))

#Plasticity Concrete Damage Plasticity (CDP)
#Plasticity parameters: dilation angle, eccentricity, fb0/fc0, K, Viscosity 
m.materials['Matrix'].ConcreteDamagedPlasticity(table=((7.86, 26.87, 32.38, 0.81, 0.074), ))
#Concrete compression hardening

m.materials['Matrix'].concreteDamagedPlasticity.ConcreteCompressionHardening(
    table=(list_ystress_vs_inelastic_com))
#print(list_ystress_vs_inelastic_com)
m.materials['Matrix'].concreteDamagedPlasticity.ConcreteTensionStiffening(
    table=(list_ystress_vs_inelastic_ten))
#print(list_damage_vs_inelastic_com)
m.materials['Matrix'].concreteDamagedPlasticity.ConcreteCompressionDamage(
    table=(list_damage_vs_inelastic_com))
#print(list_ystress_vs_inelastic_com)
m.materials['Matrix'].concreteDamagedPlasticity.ConcreteTensionDamage(
    table=(list_damage_vs_inelastic_ten))
#print(list_damage_vs_inelastic_ten)

m.Material(name='cohesive')
m.materials['cohesive'].Elastic(table=((100, 
    50, 50), ), type=TRACTION)
m.materials['cohesive'].Density(table=((1.69e-09, ), ))
m.materials['cohesive'].QuadsDamageInitiation(table=((12, 
    3.5, 3.5), ))
m.materials['cohesive'].quadsDamageInitiation.DamageEvolution(
    mixedModeBehavior=BK, power=2.0, table=((0.0002, 0.0002, 0.0002), ), type=ENERGY)
m.materials['cohesive'].quadsDamageInitiation.DamageStabilizationCohesive(
    cohesiveCoeff=0.001)
########################################################

#SECTION DEFINITIONS
m.HomogeneousSolidSection(material='Fibre', name=
    'Fibre', thickness=1)
m.HomogeneousSolidSection(material='Matrix', name=
    'Matrix', thickness=1)
m.CohesiveSection(material='cohesive', name='cohesive', initialThickness=th_coh/1000, 
    initialThicknessType=SPECIFY, outOfPlaneThickness=1, response=TRACTION_SEPARATION)


#MESH
#Create mesh

#SEED PART (MESH SIZE)
m.parts['Part-1'].seedPart(deviationFactor=0.1, 
    minSizeFactor=0.1, size=0.9/L)


##############################################################
#CREATE PARTITIONS AND ASSIGN MESH CONTROL FOR COHESIVE SECTION TO CREATE CORRECT MESH STACKING ORIENTATION

# Only create partitions if circle is completely inside the square
#CREATE PARTITIONS
#PARTITION COHESIVE ON THE EDGES RIGHT
for n in data_fibres:
    if ( ((tp1 - n[0]) < n[2]) and ((n[0] + n[2]) > tp1)):
        m.ConstrainedSketch(gridSpacing=0.004, name='__profile__', 
            sheetSize=10 * 200, transform=
            m.parts['Part-1'].MakeSketchTransform(
            sketchPlane=m.parts['Part-1'].faces.findAt((n[0]-n[2]+(th_coh/2)/L,n[1],0.0), ), 
            #sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.066716, 0.057, 0.0)))
            sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
        m.sketches['__profile__'].sketchOptions.setValues(
            decimalPlaces=5)
        m.sketches['__profile__'].Line(point1=(n[0], n[1]), point2=(
            n[0]-n[2], n[1]))
        m.sketches['__profile__'].HorizontalConstraint(
            addUndoState=False, entity=
            mdb.models['Model-1'].sketches['__profile__'].geometry[2])

        m.parts['Part-1'].PartitionFaceBySketch(faces=
            m.parts['Part-1'].faces.findAt(((n[0]-n[2]+(th_coh/2)/L,n[1],0.0), )), sketch=
            m.sketches['__profile__'])
        del m.sketches['__profile__']

    #ASSIGN MESH CONTROL FOR STACK ORIENTATION: TOP SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0] - n[2] + (th_coh/2)/L, n[1] + (th_coh/2)/L, 0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0] - n[2] + (th_coh/2)/L, n[1], 0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0] - n[2] + (th_coh/2)/L, n[1] + (th_coh/2)/L, 0.), ), sense=REVERSE)

    #ASSIGN MESH CONTROL FOR STACK ORIENTATION: BOTTOM SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0] - n[2] + (th_coh/2)/L, n[1] - (th_coh/2)/L, 0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0] - n[2] + (th_coh/2)/L, n[1], 0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0] - n[2] + (th_coh/2)/L, n[1] - (th_coh/2)/L, 0.), ), sense=REVERSE)


        #ASSIGN MESH CONTROL: TOP SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0] - n[2] + (th_coh/2)/L, n[1] + (th_coh/2)/L, 0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0] - n[2] + (th_coh/2)/L, n[1] + (th_coh/2)/L, 0.), )), ))

    #ASSIGN MESH CONTROL: BOTTOM SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0] - n[2] + (th_coh/2)/L, n[1] - (th_coh/2)/L, 0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0] - n[2] + (th_coh/2)/L, n[1] - (th_coh/2)/L, 0.), )), ))



    #PARTITION COHESIVE ON THE EDGES LEFT
    if ( ((n[0] - 0) < n[2]) and ((n[0] - n[2]) < 0)):
        m.ConstrainedSketch(gridSpacing=0.004, name='__profile__', 
            sheetSize=10 * 200, transform=
            m.parts['Part-1'].MakeSketchTransform(
            sketchPlane=m.parts['Part-1'].faces.findAt((n[0]+n[2]-(th_coh/2)/L,n[1],0.0), ), 
            #sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.066716, 0.057, 0.0)))
            sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
        m.sketches['__profile__'].sketchOptions.setValues(
            decimalPlaces=5)
        m.sketches['__profile__'].Line(point1=(n[0], n[1]), point2=(
            n[0]+n[2], n[1]))
        m.sketches['__profile__'].HorizontalConstraint(
            addUndoState=False, entity=
            mdb.models['Model-1'].sketches['__profile__'].geometry[2])

        m.parts['Part-1'].PartitionFaceBySketch(faces=
            m.parts['Part-1'].faces.findAt(((n[0]+n[2]-(th_coh/2)/L,n[1],0.0), )), sketch=
            m.sketches['__profile__'])
        del m.sketches['__profile__']

    #ASSIGN MESH CONTROL FOR STACK ORIENTATION: TOP SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0] + n[2] - (th_coh/2)/L, n[1] + (th_coh/2)/L, 0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0] + n[2] - (th_coh/2)/L, n[1], 0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0] + n[2] - (th_coh/2)/L, n[1] + (th_coh/2)/L, 0.), ), sense=REVERSE)

    #ASSIGN MESH CONTROL FOR STACK ORIENTATION: BOTTOM SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0] + n[2] - (th_coh/2)/L, n[1] - (th_coh/2)/L, 0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0] + n[2] - (th_coh/2)/L, n[1], 0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0] + n[2] - (th_coh/2)/L, n[1] - (th_coh/2)/L, 0.), ), sense=REVERSE)



        #ASSIGN MESH CONTROL: TOP SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0] + n[2] - (th_coh/2)/L, n[1] + (th_coh/2)/L, 0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0] + n[2] - (th_coh/2)/L, n[1] + (th_coh/2)/L, 0.), )), ))

    #ASSIGN MESH CONTROL: BOTTOM SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0] + n[2] - (th_coh/2)/L, n[1] - (th_coh/2)/L, 0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0] + n[2] - (th_coh/2)/L, n[1] - (th_coh/2)/L, 0.), )), ))
#########################


#PARTITION COHESIVE ON THE EDGES BOTTOM
    if ( ((n[1] - 0) < n[2]) and ((n[1] - n[2]) < 0)):
        m.ConstrainedSketch(gridSpacing=0.004, name='__profile__', 
            sheetSize=10 * 200, transform=
            m.parts['Part-1'].MakeSketchTransform(
            sketchPlane=m.parts['Part-1'].faces.findAt((n[0],n[1]+n[2]-(th_coh/2)/L,0.0), ), 
            #sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.066716, 0.057, 0.0)))
            sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
        m.sketches['__profile__'].sketchOptions.setValues(
            decimalPlaces=5)
        m.sketches['__profile__'].Line(point1=(n[0], n[1]), point2=(
            n[0], n[1]+n[2]))
        m.sketches['__profile__'].VerticalConstraint(
            addUndoState=False, entity=
            mdb.models['Model-1'].sketches['__profile__'].geometry[2])

        m.parts['Part-1'].PartitionFaceBySketch(faces=
            m.parts['Part-1'].faces.findAt(((n[0],n[1]+n[2]-(th_coh/2)/L,0.0), )), sketch=
            m.sketches['__profile__'])
        del m.sketches['__profile__']

        #ASSIGN MESH CONTROL FOR STACK ORIENTATION: LEFT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0]-(th_coh/2)/L, n[1] + n[2] - (th_coh/2)/L, 0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0], n[1] + n[2] - (th_coh/2)/L, 0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0]-(th_coh/2)/L, n[1] + n[2] - (th_coh/2)/L, 0.), ), sense=REVERSE)

    #ASSIGN MESH CONTROL FOR STACK ORIENTATION: RIGHT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0]+(th_coh/2)/L, n[1] + n[2] - (th_coh/2)/L, 0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0], n[1] + n[2] - (th_coh/2)/L, 0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0]+(th_coh/2)/L, n[1] + n[2] - (th_coh/2)/L, 0.), ), sense=REVERSE)

        #ASSIGN MESH CONTROL: RIGHT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0]+(th_coh/2)/L, n[1] + n[2] - (th_coh/2)/L, 0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0]+(th_coh/2)/L, n[1] + n[2] - (th_coh/2)/L, 0.), )), ))

    #ASSIGN MESH CONTROL: LEFT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0]-(th_coh/2)/L, n[1] + n[2] - (th_coh/2)/L, 0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0]-(th_coh/2)/L, n[1] + n[2] - (th_coh/2)/L, 0.), )), ))



#########################################################

#PARTITION COHESIVE ON THE EDGES TOP
    if ( ((tp1-n[1]) < n[2]) and ((n[1] + n[2]) > tp1)):
        m.ConstrainedSketch(gridSpacing=0.004, name='__profile__', 
            sheetSize=10 * 200, transform=
            m.parts['Part-1'].MakeSketchTransform(
            sketchPlane=m.parts['Part-1'].faces.findAt((n[0],n[1]-n[2]+(th_coh/2)/L,0.0), ), 
            #sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.066716, 0.057, 0.0)))
            sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
        m.sketches['__profile__'].sketchOptions.setValues(
            decimalPlaces=5)
        m.sketches['__profile__'].Line(point1=(n[0], n[1]), point2=(
            n[0], n[1]-n[2]))
        m.sketches['__profile__'].VerticalConstraint(
            addUndoState=False, entity=
            mdb.models['Model-1'].sketches['__profile__'].geometry[2])

        m.parts['Part-1'].PartitionFaceBySketch(faces=
            m.parts['Part-1'].faces.findAt(((n[0],n[1]-n[2]+(th_coh/2)/L,0.0), )), sketch=
            m.sketches['__profile__'])
        del m.sketches['__profile__']

    #ASSIGN MESH CONTROL FOR STACK ORIENTATION: LEFT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0]-(th_coh/2)/L, n[1] - n[2] + (th_coh/2)/L, 0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0], n[1] - n[2]+(th_coh/2)/L, 0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0]-(th_coh/2)/L, n[1] - n[2] + (th_coh/2)/L, 0.), ), sense=REVERSE)

    #ASSIGN MESH CONTROL FOR STACK ORIENTATION: RIGHT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0]+(th_coh/2)/L, n[1] - n[2] + (th_coh/2)/L, 0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0], n[1] - n[2]+(th_coh/2)/L, 0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0]+(th_coh/2)/L, n[1] - n[2] + (th_coh/2)/L, 0.), ), sense=REVERSE)

    #ASSIGN MESH CONTROL: RIGHT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0]+(th_coh/2)/L, n[1] - n[2] + (th_coh/2)/L, 0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0]+(th_coh/2)/L, n[1] - n[2] + (th_coh/2)/L, 0.), )), ))

    #ASSIGN MESH CONTROL: LEFT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0]-(th_coh/2)/L, n[1] - n[2] + (th_coh/2)/L, 0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0]-(th_coh/2)/L, n[1] - n[2] + (th_coh/2)/L, 0.), )), ))


###############################################

#FIBRES COMPLETELY INSIDE THE RVE

for n in data_fibres:
    if ( ((n[1] + n[2]) < tp1) and ((n[1] - n[2]) > 0) and ((n[0] - n[2]) > 0) and ((n[0] + n[2]) < tp1)):
        m.parts['Part-1'].PartitionFaceByShortestPath(faces=
            m.parts['Part-1'].faces.findAt(((n[0], n[2] + n[1]-(th_coh/2)/L, 
            0), )),
            point1=m.parts['Part-1'].vertices.findAt((n[0], n[2] + n[1], 
            0), ), point2=
            m.parts['Part-1'].InterestingPoint(
            m.parts['Part-1'].edges.findAt((n[0], n[1] - n[2], 
            0), ), MIDDLE))

    #ASSIGN MESH CONTROL FOR STACK ORIENTATION: LEFT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0]- n[2]+(th_coh/2)/L, n[1],0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0], n[1] - n[2]+(th_coh/2)/L,0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0]- n[2]+(th_coh/2)/L, n[1],0.), ), sense=REVERSE)

    #ASSIGN MESH CONTROL FOR STACK ORIENTATION: RIGHT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(regions=
            m.parts['Part-1'].faces.findAt(((n[0] + n[2]-(th_coh/2)/L, n[1],0.), )), technique=SWEEP)

        m.parts['Part-1'].setSweepPath(edge=
            m.parts['Part-1'].edges.findAt((n[0], n[1] - n[2]+(th_coh/2)/L,0.), ), region=
            m.parts['Part-1'].faces.findAt((n[0] + n[2]-(th_coh/2)/L, n[1],0.), ), sense=REVERSE)



######################################################
    #MESH CONTROLS FOR COHESIVE ELEMENTS: ELEMENT SHAPE AND TYPE

    #ASSIGN MESH CONTROL: RIGHT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0] + n[2]-(th_coh/2)/L, n[1],0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0] + n[2]-(th_coh/2)/L, n[1],0.), )), ))


    #ASSIGN MESH CONTROL: LEFT SIDE OF COHESIVE FACES
    # for n in data_fibres:
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0]- n[2]+(th_coh/2)/L, n[1],0.), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=COH2D4, elemLibrary=EXPLICIT, elemDeletion=ON), ElemType(elemCode=COH2D4, 
        elemLibrary=EXPLICIT), ElemType(elemCode=UNKNOWN_TRI, 
        elemLibrary=EXPLICIT)), regions=(
        m.parts['Part-1'].faces.findAt(((n[0]- n[2]+(th_coh/2)/L, n[1],0.), )), ))


########################################################################################

#####################################################
for n in data_fibres:
    #Mesh control fibres AGAIN!
    #CENTRE INSIDE
    if ( ((n[1] + n[2]) < tp1) and ((n[1] - n[2]) > 0) and ((n[0] - n[2]) > 0) and ((n[0] + n[2]) < tp1)):
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
            m.parts['Part-1'].faces.findAt(((n[0], n[1], 
            0), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=CPS4R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, 
        hourglassControl=DEFAULT, distortionControl=DEFAULT, elemDeletion=ON), 
        ElemType(elemCode=CPS4R, elemLibrary=EXPLICIT)), regions=(
        mdb.models['Model-1'].parts['Part-1'].faces.findAt(((n[0], n[1], 
            0), )),))
    
    #LEFT OUTSIDE
    if ( ((n[0] - n[2]) < 0) ):
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, algorithm=MEDIAL_AXIS, regions=
            m.parts['Part-1'].faces.findAt(((n[0]+n[2]-3.0*(th_coh/2)/L, n[1], 0), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=CPS4R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, 
        hourglassControl=DEFAULT, distortionControl=DEFAULT, elemDeletion=ON), 
        ElemType(elemCode=CPS4R, elemLibrary=EXPLICIT)), regions=(
        mdb.models['Model-1'].parts['Part-1'].faces.findAt(((n[0]+n[2]-3.0*(th_coh/2)/L, n[1], 0), )),))
    
    #RIGHT OUTSIDE
    if ( ((n[0] + n[2]) > tp1) ):
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, algorithm=MEDIAL_AXIS, regions=
            m.parts['Part-1'].faces.findAt(((n[0]-n[2]+3.0*(th_coh/2)/L, n[1], 0), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=CPS4R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, 
        hourglassControl=DEFAULT, distortionControl=DEFAULT, elemDeletion=ON), 
        ElemType(elemCode=CPS4R, elemLibrary=EXPLICIT)), regions=(
        mdb.models['Model-1'].parts['Part-1'].faces.findAt(((n[0]-n[2]+3.0*(th_coh/2)/L, n[1], 0), )),))

    #TOP OUTSIDE
    if ( ((n[1] + n[2]) > tp1) ):
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, algorithm=MEDIAL_AXIS, regions=
            m.parts['Part-1'].faces.findAt(((n[0], n[1]-n[2]+3.0*(th_coh/2)/L, 0), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=CPS4R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, 
        hourglassControl=DEFAULT, distortionControl=DEFAULT, elemDeletion=ON), 
        ElemType(elemCode=CPS4R, elemLibrary=EXPLICIT)), regions=(
        mdb.models['Model-1'].parts['Part-1'].faces.findAt(((n[0], n[1]-n[2]+3.0*(th_coh/2)/L, 0), )),))

    #BOTTOM OUTSIDE
    if ( ((n[1] - n[2]) < 0) ):
        m.parts['Part-1'].setMeshControls(elemShape=QUAD, algorithm=MEDIAL_AXIS, regions=
            m.parts['Part-1'].faces.findAt(((n[0], n[1]+n[2]-3.0*(th_coh/2)/L, 0), )))
        m.parts['Part-1'].setElementType(elemTypes=(ElemType(
        elemCode=CPS4R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, 
        hourglassControl=DEFAULT, distortionControl=DEFAULT, elemDeletion=ON), 
        ElemType(elemCode=CPS4R, elemLibrary=EXPLICIT)), regions=(
        mdb.models['Model-1'].parts['Part-1'].faces.findAt(((n[0], n[1]+n[2]-3.0*(th_coh/2)/L, 0), )),))



#MESH CONTROLS FOR MATRIX: ELEMENT SHAPE AND TYPE
m.parts['Part-1'].setMeshControls(elemShape=QUAD, regions=
    m.parts['Part-1'].faces.findAt(((0, 0, 
        0), )))
m.parts['Part-1'].setElementType(elemTypes=(ElemType(
    elemCode=CPS4R, elemLibrary=EXPLICIT, secondOrderAccuracy=ON, 
    hourglassControl=DEFAULT, distortionControl=DEFAULT, elemDeletion=ON), 
    ElemType(elemCode=CPS4R, elemLibrary=EXPLICIT)), regions=(
    mdb.models['Model-1'].parts['Part-1'].faces.findAt(((0, 0, 
        0), )),))

#RIGHT SIDE SEEDING
m.parts['Part-1'].seedEdgeBySize(constraint=FIXED, 
    deviationFactor=0.1, edges=
    m.parts['Part-1'].edges.getByBoundingBox(tp1, 0.0, 0.0, 2*tp1, tp1, 0.0), minSizeFactor=0.1, size=0.0009)

#LEFT SIDE SEEDING
m.parts['Part-1'].seedEdgeBySize(constraint=FIXED, 
    deviationFactor=0.1, edges=
    m.parts['Part-1'].edges.getByBoundingBox(-tp1, 0.0, 0.0, 0.0, tp1, 0.0), minSizeFactor=0.1, size=0.0009)

#TOP SIDE SEEDING
m.parts['Part-1'].seedEdgeBySize(constraint=FIXED, 
    deviationFactor=0.1, edges=
    m.parts['Part-1'].edges.getByBoundingBox(0.0, tp1, 0.0, tp1, 2*tp1, 0.0), minSizeFactor=0.1, size=0.0009)

#BOTTOM SIDE SEEDING
m.parts['Part-1'].seedEdgeBySize(constraint=FIXED, 
    deviationFactor=0.1, edges=
    m.parts['Part-1'].edges.getByBoundingBox(0.0, -tp1, 0.0, tp1, 0.0, 0.0), minSizeFactor=0.1, size=0.0009)



#GENERATE MESH
m.parts['Part-1'].generateMesh()
#############################################################

#CONDITION: NO FIBERS SHOULD INTERSECT THE ORIGIN (0,0,0)

m.parts['Part-1'].SectionAssignment(offset=0.0, 
    offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
    faces=m.parts['Part-1'].faces.findAt(((0, 0, 0),), )), sectionName='Matrix', thicknessAssignment=
    FROM_SECTION)

#Centre
for n in data_fibres:
    if ( ((n[1] + n[2]) < tp1) and ((n[1] - n[2]) > 0) and ((n[0] - n[2]) > 0) and ((n[0] + n[2]) < tp1)):
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0], n[1], 0),), )), sectionName='Fibre', thicknessAssignment=
        FROM_SECTION)

#LEFT
for n in data_fibres:
    if ( ((n[0] - 0) < n[2]) and ((n[0] - n[2]) < 0)):
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]+n[2]-3.0*(th_coh/2)/L, n[1], 0),), )), sectionName='Fibre', thicknessAssignment=
        FROM_SECTION)

#RIGHT
for n in data_fibres:
    if ( ((tp1 - n[0]) < n[2]) and ((n[0] + n[2]) > tp1)):
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]-n[2]+3.0*(th_coh/2)/L, n[1], 0),), )), sectionName='Fibre', thicknessAssignment=
        FROM_SECTION)

#TOP
for n in data_fibres:
    if ( ((tp1-n[1]) < n[2]) and ((n[1] + n[2]) > tp1)):
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0], n[1]-n[2]+3.0*(th_coh/2)/L, 0),), )), sectionName='Fibre', thicknessAssignment=
        FROM_SECTION)

#BOTTOM
for n in data_fibres:
    if ( ((n[1] - 0) < n[2]) and ((n[1] - n[2]) < 0)):
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0], n[1]+n[2]-3.0*(th_coh/2)/L, 0),), )), sectionName='Fibre', thicknessAssignment=
        FROM_SECTION)


#Assign material properties to COHESIVE interfaces

#CENTRE
for n in data_fibres:
    if ( ((n[1] + n[2]) < tp1) and ((n[1] - n[2]) > 0) and ((n[0] - n[2]) > 0) and ((n[0] + n[2]) < tp1)):
    #Left side of circle    
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]-n[2]+(th_coh/2)/L, n[1], 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)
    #Right side of circle    
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]+n[2]-(th_coh/2)/L, n[1], 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)



#LEFT SIDE (top)
for n in data_fibres:
    if ( ((n[0] - 0) < n[2]) and ((n[0] - n[2]) < 0)):
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]+n[2]-(th_coh/2)/L, n[1] + (th_coh/2)/L, 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)

#LEFT SIDE (bottom)

        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]+n[2]-(th_coh/2)/L, n[1] - (th_coh/2)/L, 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)

#RIGHT SIDE (top)
for n in data_fibres:
    if ( ((tp1 - n[0]) < n[2]) and ((n[0] + n[2]) > tp1)):
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]-n[2]+(th_coh/2)/L, n[1] + (th_coh/2)/L, 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)
#RIGHT SIDE (bottom)

        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]-n[2]+(th_coh/2)/L, n[1] - (th_coh/2)/L, 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)



#TOP SIDE (left)
for n in data_fibres:
    if ( ((tp1-n[1]) < n[2]) and ((n[1] + n[2]) > tp1)):
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]- (th_coh/2)/L, n[1]-n[2]+(th_coh/2)/L, 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)
#TOP SIDE (right)

        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0]+ (th_coh/2)/L, n[1]-n[2]+(th_coh/2)/L, 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)




#BOTTOM SIDE (left)
for n in data_fibres:
    if ( ((n[1] - 0) < n[2]) and ((n[1] - n[2]) < 0)):
        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0] - (th_coh/2)/L, n[1]+n[2]-(th_coh/2)/L, 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)

#BOTTOM SIDE (right)

        m.parts['Part-1'].SectionAssignment(offset=0.0, 
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=m.parts['Part-1'].faces.findAt(((n[0] + (th_coh/2)/L, n[1]+n[2]-(th_coh/2)/L, 0),), )), sectionName='cohesive', thicknessAssignment=
        FROM_SECTION)





#Regenerate assembly
a.regenerate()

###################################
#CREATE STEP

#STEP
#Create Explicit step with mass scaling every increment
m.ExplicitDynamicsStep(improvedDtMethod=ON, massScaling=((
    SEMI_AUTOMATIC, MODEL, THROUGHOUT_STEP, 0.0, 1e-06, BELOW_MIN, 1, 0, 0.0, 0.0, 
    0, None), ), timePeriod=0.2, name='Step-1', previous='Initial')

#CREATE OUTPUTS
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(numIntervals=
    40, variables=('S', 'SVAVG', 'PE', 'PEVAVG', 'PEEQ', 'PEEQVAVG', 'LE', 'E', 
    'U', 'V', 'A', 'RF', 'CSTRESS', 'EVF', 'STATUS', 'CSDMG', 'SDEG', 'DAMAGEC', 'DAMAGET', 'DMICRT', 'EVOL', 'IVOL'))

##################################
