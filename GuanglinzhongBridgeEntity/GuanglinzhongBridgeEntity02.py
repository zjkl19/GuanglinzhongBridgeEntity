# -*- coding: utf-8 -*-
# -*- coding: mbcs -*-

#summary:Guanglinzhong Bridge
#structure:Simple Support Beam
#load:Truck Load
#post:u, moment

#comment by lindinan in 20180709

from abaqus import *
from abaqusConstants import *
from caeModules import *

from interaction import *
from optimization import * 
from sketch import *
from visualization import *
from connectorBehavior import *

import regionToolset

import json

session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)

nBeams=14    #number of beams
hDist=1.25   #horizontal distance
span=20
nVirtualBeam=21    #number of the virtual beam

rouC50=2549
EC50=3.45E10
GC50=2.50E10
niuC50=0.2    #possion ratio

shellThickness=0.1  #the thickness of deck
shellWidth=18


middleBeamOutter=((0.0,0.0),(124,0),(124,25),(117,25),     
        (117,90), (7,90),(7,25),(0,25))
middleBeamOutter=[(i[0]*0.01,i[1]*0.01) for i in middleBeamOutter]

middleBeamInner=((28,12),(96,12),(96,78),(28,78))
middleBeamInner=[(i[0]*0.01,i[1]*0.01) for i in middleBeamInner]

sideBeamOutter=((0.0,0.0),(124.5,0),(124.5,73),(124.5+25,73),     
        (124.5+25,90), (7,90),(7,25),(0,25))
sideBeamOutter=[(i[0]*0.01,i[1]*0.01) for i in sideBeamOutter]

sideBeamInner=((28,12),(96,12),(96,78),(28,78))
sideBeamInner=[(i[0]*0.01,i[1]*0.01) for i in sideBeamInner]

shellOutter=((0,0),(18,0),(18,0.1),(0,0.1))

#set the beam section
def CreateBeamPart(mySketch,Outter,Inner=()):
    for i in range(0,len(Outter)):
        if(i!=len(Outter)-1):    
            mySketch.Line(point1=Outter[i], point2=Outter[i+1])
        else:
            mySketch.Line(point1=Outter[i], point2=Outter[0])
    if(len(Inner)!=0):
        for i in range(0,len(Inner)):
            if(i!=len(Inner)-1):  
                mySketch.Line(point1=Inner[i], point2=Inner[i+1])
            else:
                mySketch.Line(point1=Inner[i], point2=Inner[0])
    

# Create a model.
modelName='GuanglinzhongBridge'
myModel = mdb.Model(name=modelName)

myModel.Material(name='C50Material')
myModel.materials['C50Material'].Density(table=((rouC50,), ))
myModel.materials['C50Material'].Elastic(table=((EC50, niuC50), ))

myModel.HomogeneousSolidSection(name='C50Section',material='C50Material', thickness=None)

# Create a sketch
from part import *
middleBeamSketch = myModel.ConstrainedSketch(name='middleBeamSketch',sheetSize=300.0)

# Create the line.

#middlebeam
CreateBeamPart(middleBeamSketch,middleBeamOutter,middleBeamInner)
myPart = myModel.Part(name='middleBeamPart', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=middleBeamSketch , depth=span)


sideBeamSketch = myModel.ConstrainedSketch(name='sideBeamSketch',sheetSize=300.0)
CreateBeamPart(sideBeamSketch,sideBeamOutter,sideBeamInner)
myPart = myModel.Part(name='sideBeamPart', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=sideBeamSketch , depth=span)

shellSketch = myModel.ConstrainedSketch(name='shellSketch',sheetSize=300.0)
CreateBeamPart(shellSketch,shellOutter)
myPart = myModel.Part(name='shellPart', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=shellSketch , depth=span)

#section assignment
c = myModel.parts['middleBeamPart'].cells
cells = c.findAt(((0.05, 0.05, 13), ))
region = myModel.parts['middleBeamPart'].Set(cells=cells, name='Set-1')
myModel.parts['middleBeamPart'].SectionAssignment(region=region, sectionName='C50Section', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

c = myModel.parts['sideBeamPart'].cells
cells = c.findAt(((0.05, 0.05, 13), ))
region = myModel.parts['sideBeamPart'].Set(cells=cells, name='Set-2')
myModel.parts['sideBeamPart'].SectionAssignment(region=region, sectionName='C50Section', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

c = myModel.parts['shellPart'].cells
cells = c.findAt(((12, 0.0, 13), ))
region = myModel.parts['shellPart'].Set(cells=cells, name='Set-3')
myModel.parts['shellPart'].SectionAssignment(region=region, sectionName='C50Section', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

#Assembly
a = mdb.models['GuanglinzhongBridge'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['GuanglinzhongBridge'].parts['middleBeamPart']
a.Instance(name='middleBeamPart-1', part=p, dependent=OFF)
p = mdb.models['GuanglinzhongBridge'].parts['shellPart']
a.Instance(name='shellPart-1', part=p, dependent=OFF)
p = mdb.models['GuanglinzhongBridge'].parts['sideBeamPart']
a.Instance(name='sideBeamPart-1', part=p, dependent=OFF)

a = mdb.models['GuanglinzhongBridge'].rootAssembly
a.translate(instanceList=('shellPart-1', ), vector=(0.0, 0.9, 0.0))
#: The instance shellPart-1 was translated by 0., 900.E-03, 0. with respect to the assembly coordinate system

a = mdb.models['GuanglinzhongBridge'].rootAssembly
a.translate(instanceList=('middleBeamPart-1', ), vector=(1.505, 0.0, 0.0))
#: The instance middleBeamPart-1 was translated by 1.505, 0., 0. with respect to the assembly coordinate system
a = mdb.models['GuanglinzhongBridge'].rootAssembly
a.LinearInstancePattern(instanceList=('middleBeamPart-1', ), direction1=(1.0, 
    0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=12, number2=1, 
    spacing1=1.25, spacing2=0.9)

a = mdb.models['GuanglinzhongBridge'].rootAssembly
a.translate(instanceList=('sideBeamPart-1', ), vector=(16.505, 0.0, 0.0))
#: The instance sideBeamPart-1 was translated by 16.505, 0., 0. with respect to the assembly coordinate system

a = mdb.models['GuanglinzhongBridge'].rootAssembly
p = mdb.models['GuanglinzhongBridge'].parts['sideBeamPart']
a.Instance(name='sideBeamPart-2', part=p, dependent=OFF)
a.rotate(instanceList=('sideBeamPart-2', ), axisPoint=(0.7475, 0.0, 10.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=180.0)

a = mdb.models['GuanglinzhongBridge'].rootAssembly
a.InstanceFromBooleanMerge(name='PartAll', instances=(
    a.instances['middleBeamPart-1'], a.instances['shellPart-1'], 
    a.instances['sideBeamPart-1'], 
    a.instances['middleBeamPart-1-lin-2-1'], 
    a.instances['middleBeamPart-1-lin-3-1'], 
    a.instances['middleBeamPart-1-lin-4-1'], 
    a.instances['middleBeamPart-1-lin-5-1'], 
    a.instances['middleBeamPart-1-lin-6-1'], 
    a.instances['middleBeamPart-1-lin-7-1'], 
    a.instances['middleBeamPart-1-lin-8-1'], 
    a.instances['middleBeamPart-1-lin-9-1'], 
    a.instances['middleBeamPart-1-lin-10-1'], 
    a.instances['middleBeamPart-1-lin-11-1'], 
    a.instances['middleBeamPart-1-lin-12-1'], 
    a.instances['sideBeamPart-2'], ), 
    originalInstances=SUPPRESS, domain=GEOMETRY)

#Create Step
mdb.models['GuanglinzhongBridge'].StaticStep(name='Step-1', previous='Initial')

a = mdb.models['GuanglinzhongBridge'].rootAssembly
a.makeIndependent(instances=(a.instances['PartAll-1'], ))
dP1=a.DatumPointByCoordinate(coords=(0.25, 0.0, 0.3))
dP2=a.DatumPointByCoordinate(coords=(17.75, 0.0, 0.3))
f1 = a.instances['PartAll-1'].faces
#partition in pickedFaces
pickedFaces = f1.findAt(((0.665, 0.0, 6.666667), ), ((16.081667, 0.0, 
    13.333333), ), ((14.831667, 0.0, 13.333333), ), ((13.581667, 0.0, 
    13.333333), ), ((12.331667, 0.0, 13.333333), ), ((11.081667, 0.0, 
    13.333333), ), ((9.831667, 0.0, 13.333333), ), ((8.581667, 0.0, 13.333333), 
    ), ((7.331667, 0.0, 13.333333), ), ((6.081667, 0.0, 13.333333), ), ((
    4.831667, 0.0, 13.333333), ), ((3.581667, 0.0, 13.333333), ), ((17.335, 
    0.0, 13.333333), ), ((2.331667, 0.0, 13.333333), ))

d1 = a.datums

a.PartitionFaceByShortestPath(point1=d1[dP1.id], point2=d1[dP2.id], faces=pickedFaces)
e1 = a.instances['PartAll-1'].edges
#boundry condition in pickededges
edges1 = e1.findAt(((0.56125, 0.0, 0.3), ), ((15.565, 0.0, 0.3), ), ((14.315, 
    0.0, 0.3), ), ((13.065, 0.0, 0.3), ), ((11.815, 0.0, 0.3), ), ((10.565, 
    0.0, 0.3), ), ((9.315, 0.0, 0.3), ), ((8.065, 0.0, 0.3), ), ((6.815, 0.0, 
    0.3), ), ((5.565, 0.0, 0.3), ), ((4.315, 0.0, 0.3), ), ((3.065, 0.0, 0.3), 
    ), ((16.81625, 0.0, 0.3), ), ((1.815, 0.0, 0.3), ))
region = a.Set(edges=edges1, name='Set-1')

mdb.models['GuanglinzhongBridge'].EncastreBC(name='BC-1', 
    createStepName='Initial', region=region, localCsys=None)

dP3=a.DatumPointByCoordinate(coords=(0.25, 0.0, span-0.3))
dP4=a.DatumPointByCoordinate(coords=(17.75, 0.0, span-0.3))
f1 = a.instances['PartAll-1'].faces
pickedFaces = f1.findAt(((0.665, 0.0, 6.866667), ), ((15.668334, 0.0, 
    6.866667), ), ((14.418333, 0.0, 6.866667), ), ((13.168333, 0.0, 6.866667), 
    ), ((11.918333, 0.0, 6.866667), ), ((10.668333, 0.0, 6.866667), ), ((
    9.418333, 0.0, 6.866667), ), ((8.168333, 0.0, 6.866667), ), ((6.918333, 
    0.0, 6.866667), ), ((5.668333, 0.0, 6.866667), ), ((4.418333, 0.0, 
    6.866667), ), ((3.168333, 0.0, 6.866667), ), ((16.919999, 0.0, 6.866667), 
    ), ((1.918333, 0.0, 6.866667), ))

a.PartitionFaceByShortestPath(point1=a.datums[dP3.id], point2=a.datums[dP4.id], 
    faces=pickedFaces)

e1 = a.instances['PartAll-1'].edges
#boundry condition in pickededges
edges1 = e1.findAt(((0.56125, 0.0, span-0.3), ), ((15.565, 0.0, span-0.3), ), ((14.315, 
    0.0, span-0.3), ), ((13.065, 0.0, span-0.3), ), ((11.815, 0.0, span-0.3), ), ((10.565, 
    0.0, span-0.3), ), ((9.315, 0.0, span-0.3), ), ((8.065, 0.0, span-0.3), ), ((6.815, 0.0, 
    span-0.3), ), ((5.565, 0.0, span-0.3), ), ((4.315, 0.0, span-0.3), ), ((3.065, 0.0, span-0.3), 
    ), ((16.81625, 0.0, span-0.3), ), ((1.815, 0.0, span-0.3), ))
region = a.Set(edges=edges1, name='Set-2')

mdb.models['GuanglinzhongBridge'].PinnedBC(name='BC-2', 
    createStepName='Initial', region=region, localCsys=None)

#interaction
ref1=a.ReferencePoint(point=(9.0, 0.9, 10.0))
a = mdb.models['GuanglinzhongBridge'].rootAssembly
r1 = a.referencePoints
refPoints1=(r1[ref1.id], )
region1=a.Set(referencePoints=refPoints1, name='m_Set-3')
a = mdb.models['GuanglinzhongBridge'].rootAssembly
s1 = a.instances['PartAll-1'].faces
side1Faces1 = s1.findAt(((6.0, 1.0, 13.333333), ))
region2=a.Surface(side1Faces=side1Faces1, name='s_Surf-1')
mdb.models['GuanglinzhongBridge'].Coupling(name='Constraint-1', 
    controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE, 
    couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, 
    u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

#load
refPoints1=(r1[ref1.id], )
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['GuanglinzhongBridge'].ConcentratedForce(name='Load-1', 
    createStepName='Step-1', region=region, cf2=-200000.0, 
    distributionType=UNIFORM, field='', localCsys=None)

#mesh

settingsFile = open("AppSettings.json")
setting = json.load(settingsFile) 

a = mdb.models['GuanglinzhongBridge'].rootAssembly
partInstances =(a.instances['PartAll-1'], )
a.seedPartInstance(regions=partInstances, size=setting['MeshSettings']['size'] , deviationFactor=setting['MeshSettings']['deviationFactor'] , 
    minSizeFactor=setting['MeshSettings']['minSizeFactor'])
a = mdb.models['GuanglinzhongBridge'].rootAssembly
partInstances =(a.instances['PartAll-1'], )
a.generateMesh(regions=partInstances)