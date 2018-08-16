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


s1 = a.instances['shellPart-1'].faces
side1Faces1 = s1.findAt(((12.0, 0.9, 13), ))
region1=a.Surface(side1Faces=side1Faces1, name='m_Surf-1')

s1 = a.instances['sideBeamPart-2'].faces
side1Faces1 = s1.findAt(((0.95, 0.9, 6.666667), ))
s2 = a.instances['middleBeamPart-1'].faces
side1Faces2 = s2.findAt(((1.941667, 0.9, 13.333333), ))
s3 = a.instances['middleBeamPart-1-lin-2-1'].faces
side1Faces3 = s3.findAt(((3.191667, 0.9, 13.333333), ))
s4 = a.instances['middleBeamPart-1-lin-3-1'].faces
side1Faces4 = s4.findAt(((4.441667, 0.9, 13.333333), ))
s5 = a.instances['middleBeamPart-1-lin-4-1'].faces
side1Faces5 = s5.findAt(((5.691667, 0.9, 13.333333), ))
s6 = a.instances['middleBeamPart-1-lin-5-1'].faces
side1Faces6 = s6.findAt(((6.941667, 0.9, 13.333333), ))
s7 = a.instances['middleBeamPart-1-lin-6-1'].faces
side1Faces7 = s7.findAt(((8.191667, 0.9, 13.333333), ))
s8 = a.instances['middleBeamPart-1-lin-7-1'].faces
side1Faces8 = s8.findAt(((9.441667, 0.9, 13.333333), ))
s9 = a.instances['middleBeamPart-1-lin-8-1'].faces
side1Faces9 = s9.findAt(((10.691667, 0.9, 13.333333), ))
s10 = a.instances['middleBeamPart-1-lin-9-1'].faces
side1Faces10 = s10.findAt(((11.941667, 0.9, 13.333333), ))
s11 = a.instances['middleBeamPart-1-lin-10-1'].faces
side1Faces11 = s11.findAt(((13.191667, 0.9, 13.333333), ))
s12 = a.instances['middleBeamPart-1-lin-11-1'].faces
side1Faces12 = s12.findAt(((14.441667, 0.9, 13.333333), ))
s13 = a.instances['middleBeamPart-1-lin-12-1'].faces
side1Faces13 = s13.findAt(((15.691667, 0.9, 13.333333), ))
s14 = a.instances['sideBeamPart-1'].faces
side1Faces14 = s14.findAt(((17.05, 0.9, 13.333333), ))
region2=a.Surface(side1Faces=side1Faces1+side1Faces2+side1Faces3+side1Faces4+\
    side1Faces5+side1Faces6+side1Faces7+side1Faces8+side1Faces9+side1Faces10+\
    side1Faces11+side1Faces12+side1Faces13+side1Faces14, name='s_Surf-2')

myModel.Tie(name='Constraint-1', master=region1, 
    slave=region2, positionToleranceMethod=COMPUTED, adjust=ON, 
    tieRotations=ON, thickness=ON)

a = mdb.models['GuanglinzhongBridge'].rootAssembly
for i in range(0,5):
    s1 = a.instances['middleBeamPart-1-lin-' + str(7-i) +'-1'].faces
    side1Faces1 = s1.findAt(((9.075-1.25*i, 0.5, 13), ))
    region1=regionToolset.Region(side1Faces=side1Faces1)
    s1 = a.instances['middleBeamPart-1-lin-'+ str(6-i) +'-1'].faces
    side1Faces1 = s1.findAt(((8.925-1.25*i, 0.5, 13), ))
    region2=regionToolset.Region(side1Faces=side1Faces1)
    mdb.models['GuanglinzhongBridge'].Tie(name='Constraint-'+str(i+2), master=region1, 
        slave=region2, positionToleranceMethod=COMPUTED, adjust=ON, 
        tieRotations=ON, thickness=ON)

a = mdb.models['GuanglinzhongBridge'].rootAssembly
for i in range(0,5):   
    s1 = a.instances['middleBeamPart-1-lin-' + str(7+i) +'-1'].faces
    side1Faces1 = s1.findAt(((10.175+1.25*i, 0.5, 13), ))
    region1=regionToolset.Region(side1Faces=side1Faces1)
    s1 = a.instances['middleBeamPart-1-lin-' + str(8+i) +'-1'].faces
    side1Faces1 = s1.findAt(((10.325+1.25*i, 0.5, 13), ))
    region2=regionToolset.Region(side1Faces=side1Faces1)
    mdb.models['GuanglinzhongBridge'].Tie(name='Constraint-'+str(i+7), master=region1, 
        slave=region2, positionToleranceMethod=COMPUTED, adjust=ON, 
        tieRotations=ON, thickness=ON)

a = mdb.models['GuanglinzhongBridge'].rootAssembly
s1 = a.instances['middleBeamPart-1-lin-2-1'].faces
side1Faces1 = s1.findAt(((2.825, 0.466667, 13.333333), ))
region1=regionToolset.Region(side1Faces=side1Faces1)
s1 = a.instances['middleBeamPart-1'].faces
side1Faces1 = s1.findAt(((2.675, 0.683333, 13.333333), ))
region2=regionToolset.Region(side1Faces=side1Faces1)
mdb.models['GuanglinzhongBridge'].Tie(name='Constraint-12', master=region1, 
    slave=region2, positionToleranceMethod=COMPUTED, adjust=ON, 
    tieRotations=ON, thickness=ON)

s1 = a.instances['middleBeamPart-1'].faces
side1Faces1 = s1.findAt(((1.575, 0.466667, 13.333333), ))
region1=regionToolset.Region(side1Faces=side1Faces1)
s1 = a.instances['sideBeamPart-2'].faces
side1Faces1 = s1.findAt(((1.425, 0.466667, 6.666667), ))
region2=regionToolset.Region(side1Faces=side1Faces1)
mdb.models['GuanglinzhongBridge'].Tie(name='Constraint-13', master=region1, 
    slave=region2, positionToleranceMethod=COMPUTED, adjust=ON, 
    tieRotations=ON, thickness=ON)

a = mdb.models['GuanglinzhongBridge'].rootAssembly
s1 = a.instances['middleBeamPart-1-lin-12-1'].faces
side1Faces1 = s1.findAt(((16.425, 0.683333, 13.333333), ))
region1=regionToolset.Region(side1Faces=side1Faces1)
s1 = a.instances['sideBeamPart-1'].faces
side1Faces1 = s1.findAt(((16.575, 0.466667, 13.333333), ))
region2=regionToolset.Region(side1Faces=side1Faces1)
mdb.models['GuanglinzhongBridge'].Tie(name='Constraint-14', master=region1, 
    slave=region2, positionToleranceMethod=COMPUTED, adjust=ON, 
    tieRotations=ON, thickness=ON)


#a = mdb.models['GuanglinzhongBridge'].rootAssembly
#a.InstanceFromBooleanMerge(name='PartAll', instances=(
#    a.instances['middleBeamPart-1'], a.instances['shellPart-1'], 
#    a.instances['sideBeamPart-1'], 
#    a.instances['middleBeamPart-1-lin-2-1'], 
#    a.instances['middleBeamPart-1-lin-3-1'], 
#    a.instances['middleBeamPart-1-lin-4-1'], 
#    a.instances['middleBeamPart-1-lin-5-1'], 
#    a.instances['middleBeamPart-1-lin-6-1'], 
#    a.instances['middleBeamPart-1-lin-7-1'], 
#    a.instances['middleBeamPart-1-lin-8-1'], 
#    a.instances['middleBeamPart-1-lin-9-1'], 
#    a.instances['middleBeamPart-1-lin-10-1'], 
#    a.instances['middleBeamPart-1-lin-11-1'], 
#    a.instances['middleBeamPart-1-lin-12-1'], 
#    a.instances['sideBeamPart-2'], ), 
#    originalInstances=SUPPRESS, domain=GEOMETRY)

#Create Step
mdb.models['GuanglinzhongBridge'].StaticStep(name='Step-1', previous='Initial')

a = mdb.models['GuanglinzhongBridge'].rootAssembly
#a.makeIndependent(instances=(a.instances['PartAll-1'], ))
dP1=a.DatumPointByCoordinate(coords=(0.25, 0.0, 0.3))
dP2=a.DatumPointByCoordinate(coords=(17.75, 0.0, 0.3))

a = mdb.models['GuanglinzhongBridge'].rootAssembly
f1 = a.instances['sideBeamPart-2'].faces
faces1 = f1.findAt(((0.665, 0.0, 6.666667), ))
f2 = a.instances['middleBeamPart-1'].faces
faces2 = f2.findAt(((2.331667, 0.0, 13.333333), ))
f3 = a.instances['middleBeamPart-1-lin-2-1'].faces
faces3 = f3.findAt(((3.581667, 0.0, 13.333333), ))
f4 = a.instances['middleBeamPart-1-lin-3-1'].faces
faces4 = f4.findAt(((4.831667, 0.0, 13.333333), ))
f5 = a.instances['middleBeamPart-1-lin-4-1'].faces
faces5 = f5.findAt(((6.081667, 0.0, 13.333333), ))
f6 = a.instances['middleBeamPart-1-lin-5-1'].faces
faces6 = f6.findAt(((7.331667, 0.0, 13.333333), ))
f7 = a.instances['middleBeamPart-1-lin-6-1'].faces
faces7 = f7.findAt(((8.581667, 0.0, 13.333333), ))
f8 = a.instances['middleBeamPart-1-lin-7-1'].faces
faces8 = f8.findAt(((9.831667, 0.0, 13.333333), ))
f9 = a.instances['middleBeamPart-1-lin-8-1'].faces
faces9 = f9.findAt(((11.081667, 0.0, 13.333333), ))
f10 = a.instances['middleBeamPart-1-lin-9-1'].faces
faces10 = f10.findAt(((12.331667, 0.0, 13.333333), ))
f11 = a.instances['middleBeamPart-1-lin-10-1'].faces
faces11 = f11.findAt(((13.581667, 0.0, 13.333333), ))
f12 = a.instances['middleBeamPart-1-lin-11-1'].faces
faces12 = f12.findAt(((14.831667, 0.0, 13.333333), ))
f13 = a.instances['middleBeamPart-1-lin-12-1'].faces
faces13 = f13.findAt(((16.081667, 0.0, 13.333333), ))
f14 = a.instances['sideBeamPart-1'].faces
faces14 = f14.findAt(((17.335, 0.0, 13.333333), ))
pickedFaces = faces1+faces2+faces3+faces4+faces5+faces6+faces7+faces8+faces9+\
    faces10+faces11+faces12+faces13+faces14
d1 = a.datums
a.PartitionFaceByShortestPath(point1=d1[dP1.id], point2=d1[dP2.id], faces=pickedFaces)


#f1 = a.instances['PartAll-1'].faces
##partition in pickedFaces
#pickedFaces = f1.findAt(((0.665, 0.0, 6.666667), ), ((16.081667, 0.0, 
#    13.333333), ), ((14.831667, 0.0, 13.333333), ), ((13.581667, 0.0, 
#    13.333333), ), ((12.331667, 0.0, 13.333333), ), ((11.081667, 0.0, 
#    13.333333), ), ((9.831667, 0.0, 13.333333), ), ((8.581667, 0.0, 13.333333), 
#    ), ((7.331667, 0.0, 13.333333), ), ((6.081667, 0.0, 13.333333), ), ((
#    4.831667, 0.0, 13.333333), ), ((3.581667, 0.0, 13.333333), ), ((17.335, 
#    0.0, 13.333333), ), ((2.331667, 0.0, 13.333333), ))

#d1 = a.datums

#a.PartitionFaceByShortestPath(point1=d1[dP1.id], point2=d1[dP2.id], faces=pickedFaces)
#e1 = a.instances['PartAll-1'].edges
##boundry condition in pickededges
#edges1 = e1.findAt(((0.56125, 0.0, 0.3), ), ((15.565, 0.0, 0.3), ), ((14.315, 
#    0.0, 0.3), ), ((13.065, 0.0, 0.3), ), ((11.815, 0.0, 0.3), ), ((10.565, 
#    0.0, 0.3), ), ((9.315, 0.0, 0.3), ), ((8.065, 0.0, 0.3), ), ((6.815, 0.0, 
#    0.3), ), ((5.565, 0.0, 0.3), ), ((4.315, 0.0, 0.3), ), ((3.065, 0.0, 0.3), 
#    ), ((16.81625, 0.0, 0.3), ), ((1.815, 0.0, 0.3), ))
#region = a.Set(edges=edges1, name='Set-1')

#mdb.models['GuanglinzhongBridge'].EncastreBC(name='BC-1', 
#    createStepName='Initial', region=region, localCsys=None)

dP3=a.DatumPointByCoordinate(coords=(0.25, 0.0, span-0.3))
dP4=a.DatumPointByCoordinate(coords=(17.75, 0.0, span-0.3))

f1 = a.instances['sideBeamPart-2'].faces
faces1 = f1.findAt(((0.665, 0.0, 6.666667), ))
f2 = a.instances['middleBeamPart-1'].faces
faces2 = f2.findAt(((2.331667, 0.0, 13.333333), ))
f3 = a.instances['middleBeamPart-1-lin-2-1'].faces
faces3 = f3.findAt(((3.581667, 0.0, 13.333333), ))
f4 = a.instances['middleBeamPart-1-lin-3-1'].faces
faces4 = f4.findAt(((4.831667, 0.0, 13.333333), ))
f5 = a.instances['middleBeamPart-1-lin-4-1'].faces
faces5 = f5.findAt(((6.081667, 0.0, 13.333333), ))
f6 = a.instances['middleBeamPart-1-lin-5-1'].faces
faces6 = f6.findAt(((7.331667, 0.0, 13.333333), ))
f7 = a.instances['middleBeamPart-1-lin-6-1'].faces
faces7 = f7.findAt(((8.581667, 0.0, 13.333333), ))
f8 = a.instances['middleBeamPart-1-lin-7-1'].faces
faces8 = f8.findAt(((9.831667, 0.0, 13.333333), ))
f9 = a.instances['middleBeamPart-1-lin-8-1'].faces
faces9 = f9.findAt(((11.081667, 0.0, 13.333333), ))
f10 = a.instances['middleBeamPart-1-lin-9-1'].faces
faces10 = f10.findAt(((12.331667, 0.0, 13.333333), ))
f11 = a.instances['middleBeamPart-1-lin-10-1'].faces
faces11 = f11.findAt(((13.581667, 0.0, 13.333333), ))
f12 = a.instances['middleBeamPart-1-lin-11-1'].faces
faces12 = f12.findAt(((14.831667, 0.0, 13.333333), ))
f13 = a.instances['middleBeamPart-1-lin-12-1'].faces
faces13 = f13.findAt(((16.081667, 0.0, 13.333333), ))
f14 = a.instances['sideBeamPart-1'].faces
faces14 = f14.findAt(((17.335, 0.0, 13.333333), ))
pickedFaces = faces1+faces2+faces3+faces4+faces5+faces6+faces7+faces8+faces9+\
    faces10+faces11+faces12+faces13+faces14
d1 = a.datums
a.PartitionFaceByShortestPath(point1=d1[dP3.id], point2=d1[dP4.id], faces=pickedFaces)

a = mdb.models['GuanglinzhongBridge'].rootAssembly
e1 = a.instances['sideBeamPart-2'].edges
edges1 = e1.findAt(((1.18375, 0.0, 19.7), ))
e2 = a.instances['middleBeamPart-1'].edges
edges2 = e2.findAt(((2.435, 0.0, 19.7), ))
e3 = a.instances['middleBeamPart-1-lin-2-1'].edges
edges3 = e3.findAt(((3.685, 0.0, 19.7), ))
e4 = a.instances['middleBeamPart-1-lin-3-1'].edges
edges4 = e4.findAt(((4.935, 0.0, 19.7), ))
e5 = a.instances['middleBeamPart-1-lin-4-1'].edges
edges5 = e5.findAt(((6.185, 0.0, 19.7), ))
e6 = a.instances['middleBeamPart-1-lin-5-1'].edges
edges6 = e6.findAt(((7.435, 0.0, 19.7), ))
e7 = a.instances['middleBeamPart-1-lin-6-1'].edges
edges7 = e7.findAt(((8.685, 0.0, 19.7), ))
e8 = a.instances['middleBeamPart-1-lin-7-1'].edges
edges8 = e8.findAt(((9.935, 0.0, 19.7), ))
e9 = a.instances['middleBeamPart-1-lin-8-1'].edges
edges9 = e9.findAt(((11.185, 0.0, 19.7), ))
e10 = a.instances['middleBeamPart-1-lin-9-1'].edges
edges10 = e10.findAt(((12.435, 0.0, 19.7), ))
e11 = a.instances['middleBeamPart-1-lin-10-1'].edges
edges11 = e11.findAt(((13.685, 0.0, 19.7), ))
e12 = a.instances['middleBeamPart-1-lin-11-1'].edges
edges12 = e12.findAt(((14.935, 0.0, 19.7), ))
e13 = a.instances['middleBeamPart-1-lin-12-1'].edges
edges13 = e13.findAt(((16.185, 0.0, 19.7), ))
e14 = a.instances['sideBeamPart-1'].edges
edges14 = e14.findAt(((17.43875, 0.0, 19.7), ))
region = regionToolset.Region(edges=edges1+edges2+edges3+edges4+edges5+edges6+\
    edges7+edges8+edges9+edges10+edges11+edges12+edges13+edges14)
mdb.models['GuanglinzhongBridge'].EncastreBC(name='BC-1', 
    createStepName='Initial', region=region, localCsys=None)

a = mdb.models['GuanglinzhongBridge'].rootAssembly
e1 = a.instances['sideBeamPart-2'].edges
edges1 = e1.findAt(((1.18375, 0.0, 0.3), ))
e2 = a.instances['middleBeamPart-1'].edges
edges2 = e2.findAt(((2.435, 0.0, 0.3), ))
e3 = a.instances['middleBeamPart-1-lin-2-1'].edges
edges3 = e3.findAt(((3.685, 0.0, 0.3), ))
e4 = a.instances['middleBeamPart-1-lin-3-1'].edges
edges4 = e4.findAt(((4.935, 0.0, 0.3), ))
e5 = a.instances['middleBeamPart-1-lin-4-1'].edges
edges5 = e5.findAt(((6.185, 0.0, 0.3), ))
e6 = a.instances['middleBeamPart-1-lin-5-1'].edges
edges6 = e6.findAt(((7.435, 0.0, 0.3), ))
e7 = a.instances['middleBeamPart-1-lin-6-1'].edges
edges7 = e7.findAt(((8.685, 0.0, 0.3), ))
e8 = a.instances['middleBeamPart-1-lin-7-1'].edges
edges8 = e8.findAt(((9.935, 0.0, 0.3), ))
e9 = a.instances['middleBeamPart-1-lin-8-1'].edges
edges9 = e9.findAt(((11.185, 0.0, 0.3), ))
e10 = a.instances['middleBeamPart-1-lin-9-1'].edges
edges10 = e10.findAt(((12.435, 0.0, 0.3), ))
e11 = a.instances['middleBeamPart-1-lin-10-1'].edges
edges11 = e11.findAt(((13.685, 0.0, 0.3), ))
e12 = a.instances['middleBeamPart-1-lin-11-1'].edges
edges12 = e12.findAt(((14.935, 0.0, 0.3), ))
e13 = a.instances['middleBeamPart-1-lin-12-1'].edges
edges13 = e13.findAt(((16.185, 0.0, 0.3), ))
e14 = a.instances['sideBeamPart-1'].edges
edges14 = e14.findAt(((17.43875, 0.0, 0.3), ))
region = regionToolset.Region(edges=edges1+edges2+edges3+edges4+edges5+edges6+\
    edges7+edges8+edges9+edges10+edges11+edges12+edges13+edges14)
mdb.models['GuanglinzhongBridge'].PinnedBC(name='BC-2', 
    createStepName='Step-1', region=region, localCsys=None)

#f1 = a.instances['PartAll-1'].faces
#pickedFaces = f1.findAt(((0.665, 0.0, 6.866667), ), ((15.668334, 0.0, 
#    6.866667), ), ((14.418333, 0.0, 6.866667), ), ((13.168333, 0.0, 6.866667), 
#    ), ((11.918333, 0.0, 6.866667), ), ((10.668333, 0.0, 6.866667), ), ((
#    9.418333, 0.0, 6.866667), ), ((8.168333, 0.0, 6.866667), ), ((6.918333, 
#    0.0, 6.866667), ), ((5.668333, 0.0, 6.866667), ), ((4.418333, 0.0, 
#    6.866667), ), ((3.168333, 0.0, 6.866667), ), ((16.919999, 0.0, 6.866667), 
#    ), ((1.918333, 0.0, 6.866667), ))

#a.PartitionFaceByShortestPath(point1=a.datums[dP3.id], point2=a.datums[dP4.id], 
#    faces=pickedFaces)

#e1 = a.instances['PartAll-1'].edges
##boundry condition in pickededges
#edges1 = e1.findAt(((0.56125, 0.0, span-0.3), ), ((15.565, 0.0, span-0.3), ), ((14.315, 
#    0.0, span-0.3), ), ((13.065, 0.0, span-0.3), ), ((11.815, 0.0, span-0.3), ), ((10.565, 
#    0.0, span-0.3), ), ((9.315, 0.0, span-0.3), ), ((8.065, 0.0, span-0.3), ), ((6.815, 0.0, 
#    span-0.3), ), ((5.565, 0.0, span-0.3), ), ((4.315, 0.0, span-0.3), ), ((3.065, 0.0, span-0.3), 
#    ), ((16.81625, 0.0, span-0.3), ), ((1.815, 0.0, span-0.3), ))
#region = a.Set(edges=edges1, name='Set-2')

#mdb.models['GuanglinzhongBridge'].PinnedBC(name='BC-2', 
#    createStepName='Initial', region=region, localCsys=None)

#interaction
#a = mdb.models['GuanglinzhongBridge'].rootAssembly
#ref1=a.ReferencePoint(point=(9.0, 1.0, 10.0))
#r1 = a.referencePoints
#refPoints1=(r1[ref1.id], )
#region1=a.Set(referencePoints=refPoints1, name='m_Set-3')
#s1 = a.instances['shellPart-1'].faces
#side1Faces1 = s1.findAt(((6.0, 1.0, 13.333333), ))
#region2=a.Surface(side1Faces=side1Faces1, name='s_Surf-29')
#mdb.models['GuanglinzhongBridge'].Coupling(name='Constraint-RP1', 
#    controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE, 
#    couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, 
#    u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

a = mdb.models['GuanglinzhongBridge'].rootAssembly

#ref1=a.ReferencePoint(point=(9.0, 1.0, 10.0))
#r1 = a.referencePoints
#refPoints1=(r1[ref1.id], )
#region1=a.Set(referencePoints=refPoints1, name='m_Set-3')
#s1 = a.instances['shellPart-1'].faces
#side1Faces1 = s1.findAt(((6.0, 1.0, 13.333333), ))
#region2=a.Surface(side1Faces=side1Faces1, name='s_Surf-29')
#mdb.models['GuanglinzhongBridge'].Coupling(name='Constraint-RP1', 
#    controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE, 
#    couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, 
#    u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

#tuplePoint=((8.475,1,5),(6.575,1,5),(8.475,1,8.65),(6.575,1,8.65),(8.475,1,10),(6.575,1,10),
#    (3.375,1,5),(5.275,1,5),(3.375,1,8.65),(5.275,1,8.65),(3.375,1,10),(5.275,1,10),
#    (3.375,1,14),(5.275,1,14),(3.375,1,15.35),(5.275,1,15.35),(3.375,1,19),(5.275,1,19))

#tupleLoad=(-41890,-41890,-83780,-83780,-83780,-83780,-43750,-43750,-87500,-87500,-87500,
#    -87500,-89440,-89440,-89440,-89440,-44720,-44720)

#for i in range(0,len(tuplePoint)):
#    ref1=a.ReferencePoint(point=tuplePoint[i])
#    r1 = a.referencePoints
#    refPoints1=(r1[ref1.id], )
#    region1=a.Set(referencePoints=refPoints1, name='m_Set-'+str(i+30))
#    s1 = a.instances['shellPart-1'].faces
#    side1Faces1 = s1.findAt(((6.0, 1.0, 13), ))
#    region2=a.Surface(side1Faces=side1Faces1, name='s_Surf-'+str(i+30))
#    mdb.models['GuanglinzhongBridge'].Coupling(name='Constraint-RP'+str(i+1), 
#        controlPoint=region1, surface=region2, influenceRadius=0.002, 
#        couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, 
#        u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

#    region = regionToolset.Region(referencePoints=refPoints1)
#    mdb.models['GuanglinzhongBridge'].ConcentratedForce(name='Load-'+str(i+1), 
#        createStepName='Step-1', region=region, cf2=tupleLoad[i], 
#        distributionType=UNIFORM, field='', localCsys=None)

#ref1=a.ReferencePoint(point=(9.0, 1.0, 10.0))
#a = mdb.models['GuanglinzhongBridge'].rootAssembly
#r1 = a.referencePoints
#refPoints1=(r1[ref1.id], )
#region1=a.Set(referencePoints=refPoints1, name='m_Set-3')
#a = mdb.models['GuanglinzhongBridge'].rootAssembly
#s1 = a.instances['PartAll-1'].faces
#side1Faces1 = s1.findAt(((6.0, 1.0, 13.333333), ))
#region2=a.Surface(side1Faces=side1Faces1, name='s_Surf-1')
#mdb.models['GuanglinzhongBridge'].Coupling(name='Constraint-RP1', 
#    controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE, 
#    couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, 
#    u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

#load
#refPoints1=(r1[ref1.id], )
#region = regionToolset.Region(referencePoints=refPoints1)
#mdb.models['GuanglinzhongBridge'].ConcentratedForce(name='Load-1', 
#    createStepName='Step-1', region=region, cf2=-200000.0, 
#    distributionType=UNIFORM, field='', localCsys=None)

#mesh
#from mesh import *

#elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, 
#    kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF, 
#    hourglassControl=DEFAULT, distortionControl=DEFAULT)
#elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD, 
#    secondOrderAccuracy=OFF, distortionControl=DEFAULT)
#elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD, 
#    secondOrderAccuracy=OFF, distortionControl=DEFAULT)
#a = mdb.models['GuanglinzhongBridge'].rootAssembly
#c1 = a.instances['middleBeamPart-1'].cells
#cells1 = c1.findAt(((2.698333, 0.25, 13.333333), ))
#c2 = a.instances['shellPart-1'].cells
#cells2 = c2.findAt(((12.0, 0.9, 13.333333), ))
#c3 = a.instances['sideBeamPart-1'].cells
#cells3 = c3.findAt(((17.916667, 0.73, 13.333333), ))
#c4 = a.instances['middleBeamPart-1-lin-2-1'].cells
#cells4 = c4.findAt(((3.948333, 0.25, 13.333333), ))
#c5 = a.instances['middleBeamPart-1-lin-3-1'].cells
#cells5 = c5.findAt(((5.198333, 0.25, 13.333333), ))
#c6 = a.instances['middleBeamPart-1-lin-4-1'].cells
#cells6 = c6.findAt(((6.448333, 0.25, 13.333333), ))
#c7 = a.instances['middleBeamPart-1-lin-5-1'].cells
#cells7 = c7.findAt(((7.698333, 0.25, 13.333333), ))
#c8 = a.instances['middleBeamPart-1-lin-6-1'].cells
#cells8 = c8.findAt(((8.948333, 0.25, 13.333333), ))
#c9 = a.instances['middleBeamPart-1-lin-7-1'].cells
#cells9 = c9.findAt(((10.198333, 0.25, 13.333333), ))
#c10 = a.instances['middleBeamPart-1-lin-8-1'].cells
#cells10 = c10.findAt(((11.448333, 0.25, 13.333333), ))
#c11 = a.instances['middleBeamPart-1-lin-9-1'].cells
#cells11 = c11.findAt(((12.698333, 0.25, 13.333333), ))
#c12 = a.instances['middleBeamPart-1-lin-10-1'].cells
#cells12 = c12.findAt(((13.948333, 0.25, 13.333333), ))
#c13 = a.instances['middleBeamPart-1-lin-11-1'].cells
#cells13 = c13.findAt(((15.198333, 0.25, 13.333333), ))
#c14 = a.instances['middleBeamPart-1-lin-12-1'].cells
#cells14 = c14.findAt(((16.448333, 0.25, 13.333333), ))
#c15 = a.instances['sideBeamPart-2'].cells
#cells15 = c15.findAt(((0.0, 0.843333, 6.666667), ))
#pickedRegions =((cells1+cells2+cells3+cells4+cells5+cells6+cells7+cells8+\
#    cells9+cells10+cells11+cells12+cells13+cells14+cells15), )
#a.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, 
#    elemType3))

##a = mdb.models['GuanglinzhongBridge'].rootAssembly
#partInstances =(a.instances['middleBeamPart-1'], a.instances['shellPart-1'], 
#    a.instances['sideBeamPart-1'], a.instances['middleBeamPart-1-lin-2-1'], 
#    a.instances['middleBeamPart-1-lin-3-1'], 
#    a.instances['middleBeamPart-1-lin-4-1'], 
#    a.instances['middleBeamPart-1-lin-5-1'], 
#    a.instances['middleBeamPart-1-lin-6-1'], 
#    a.instances['middleBeamPart-1-lin-7-1'], 
#    a.instances['middleBeamPart-1-lin-8-1'], 
#    a.instances['middleBeamPart-1-lin-9-1'], 
#    a.instances['middleBeamPart-1-lin-10-1'], 
#    a.instances['middleBeamPart-1-lin-11-1'], 
#    a.instances['middleBeamPart-1-lin-12-1'], a.instances['sideBeamPart-2'], )
#a.seedPartInstance(regions=partInstances, size=0.2, deviationFactor=0.1, 
#    minSizeFactor=0.1)

#a.generateMesh(regions=partInstances)

#settingsFile = open("AppSettings.json")
#setting = json.load(settingsFile) 

#a = mdb.models['GuanglinzhongBridge'].rootAssembly
#partInstances =(a.instances['PartAll-1'], )
#a.seedPartInstance(regions=partInstances, size=setting['MeshSettings']['size'] , deviationFactor=setting['MeshSettings']['deviationFactor'] , 
#    minSizeFactor=setting['MeshSettings']['minSizeFactor'])
#a = mdb.models['GuanglinzhongBridge'].rootAssembly
#partInstances =(a.instances['PartAll-1'], )
#a.generateMesh(regions=partInstances)