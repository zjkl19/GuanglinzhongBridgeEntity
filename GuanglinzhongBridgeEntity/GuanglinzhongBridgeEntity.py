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

session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)

nBeams=14    #number of beams
hDist=1.25   #horizontal distance
span=20
nVirtualBeam=21    #number of the virtual beam

rouC50=2549
EC50=3.45E10
GC50=2.50E10
niuC50=0.2    #possion ratio


middleBeamOutter=((0.0,0.0),(124,0),(124,25),(117,25),     
        (117,90), (7,90),(7,25),(0,25))
middleBeamOutter=[(i[0]*0.01,i[1]*0.01) for i in middleBeamOutter]

middleBeamInner=((28,12),(96,12),(96,78),(28,78))
middleBeamInner=[(i[0]*0.01,i[1]*0.01) for i in middleBeamInner]

sideBeamOutter=((0.0,0.0),(124,0),(124,73),(124,73),     
        (124,90), (7,90),(7,25),(0,25))
sideBeamOutter=[(i[0]*0.01,i[1]*0.01) for i in sideBeamOutter]

sideBeamInner=((28,12),(96,12),(96,78),(28,78))
sideBeamInner=[(i[0]*0.01,i[1]*0.01) for i in sideBeamInner]

#set the beam section
def CreateBeamPart(mySketch,Outter,Inner):
    for i in range(0,len(Outter)):
        if(i!=len(Outter)-1):    
            mySketch.Line(point1=Outter[i], point2=Outter[i+1])
        else:
            mySketch.Line(point1=Outter[i], point2=Outter[0])

    for i in range(0,len(Inner)):
        if(i!=len(Inner)-1):  
            mySketch.Line(point1=Inner[i], point2=Inner[i+1])
        else:
            mySketch.Line(point1=Inner[i], point2=Inner[0])
    

# Create a model.
modelName='GuanglinzhongBridge'
myModel = mdb.Model(name=modelName)

# Create a sketch
from part import *
mySketch = myModel.ConstrainedSketch(name='mySketch',sheetSize=300.0)

# Create the line.

#middlebeam
CreateBeamPart(mySketch,middleBeamOutter,middleBeamInner)
myPart = myModel.Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=mySketch , depth=span)
del mdb.models['GuanglinzhongBridge'].sketches['mySketch']

mySketch = myModel.ConstrainedSketch(name='mySketch',sheetSize=300.0)
CreateBeamPart(mySketch,sideBeamOutter,sideBeamInner)
myPart = myModel.Part(name='Part-2', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=mySketch , depth=span)
del mdb.models['GuanglinzhongBridge'].sketches['mySketch']
#for i in range(0,len(middleBeamOutter)):
#    if(i!=len(middleBeamOutter)-1):    
#        mySketch.Line(point1=middleBeamOutter[i], point2=middleBeamOutter[i+1])
#    else:
#        mySketch.Line(point1=middleBeamOutter[i], point2=middleBeamOutter[0])

#for i in range(0,len(middleBeamInner)):
#    if(i!=len(middleBeamInner)-1):  
#        mySketch.Line(point1=middleBeamInner[i], point2=middleBeamInner[i+1])
#    else:
#        mySketch.Line(point1=middleBeamInner[i], point2=middleBeamInner[0])

# Create a three-dimensional, deformable part.

