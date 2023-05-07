#!/usr/bin/python3

import time
import math
import RPi.GPIO as GPIO
from gpiozero import MCP3008

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("fruits-freshness-detecti-8ee23-firebase-adminsdk-if92k-715c5da6af.json")
firebase_admin.initialize_app(cred)
firestore_client = firestore.client()
db = firestore_client.collection(u'sensors')
db2 = firestore_client.collection(u"User").document("EWJrHpGXFvb2Zi09W3HJId3ssFu2").collection("Fruits")

def updateSensor(mq4,mq3,mq9,mq8):
    doc = db.document("Apple")
    doc.update({
        "Ethylene" : mq3,
        "CarbonMono" : mq9,
        "Methane" : mq4,
        "Hydrogen" : mq8
    })
    

def getR0():
    #set loop values to 0:
    value=0
    x=0
    
    for x in range (0,500): #get 500 consecutive readings
        value = value + adc1.raw_value #add all readings together
        x=x+1 #increase loop counter by 1
    
    sensorValue = value/500 #calculate the adc average value from 500 readings
    sensorVolt = ((sensorValue / 1023.0) * 3.3) #convert raw adc values to voltage

    #calculate R0 (sensor resistance in clean air)
    RSair = ((3.3*10)/sensorVolt)-10 #10 (load resistance or RL) value is taken from the datasheet
    R0=RSair/9.7 #from the datasheet Rs/R0 for clean air is constant, see graph (~9.7ppm)
    print ("Calculated R0: {:.5}".format (R0))
    return R0
 
def calculatePPM(adc,R0):
    LPGm = -0.47 #slope (m)
    LPGb = 1.31 #y-intercept (b)
    sensorValue = adc
    sensorVolt = ((sensorValue / 1023.0) * 3.3)
    RSgas = ((3.3*10)/sensorVolt)- 10
    ratio = (RSgas/R0)
    
    if ratio<=0.00000:
        return ratio
    
    LPGlog =(math.log10(ratio)-LPGb)/LPGm
    LPGppm = math.pow(10,LPGlog)
#   LPGperc=LPGppm/10000
    
    return LPGppm


adc1 = MCP3008(channel=1)
adc3 = MCP3008(channel = 3)
adc5 = MCP3008(channel=5)
adc7 = MCP3008(channel = 7)
R0 = getR0()

while True:


    
    mq9Value = str(calculatePPM(adc1.raw_value,R0))
    mq4Value = str(calculatePPM(adc3.raw_value,R0))
    mq3Value = str(calculatePPM(adc5.raw_value,R0))
    mq8Value = str(calculatePPM(adc7.raw_value,R0))
    

    updateSensor("{:.4}".format(mq4Value),"{:.4}".format(mq3Value),"{:.4}".format(mq9Value),"{:.4}".format(mq8Value))
    
    
    
    print ("MQ9: {:.4}ppm   MQ4: {:.4}ppm   MQ3: {:.4}ppm   MQ8: {:.4}ppm".format(mq9Value,mq4Value,mq3Value,mq8Value))
    print("---------------------------------------------------------------------------")
    #print ("LPG percent: {:.3}%".format (LPGperc))
    time.sleep(3)
