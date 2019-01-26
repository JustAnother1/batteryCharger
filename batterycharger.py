#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import usbTemperature
import powerSupply
import time
import threading
import pprint

# NiMH AAA
NiMH_Cfg = {'curLimit' : '0.1', 'voltLimit' : '1.6', 'timeout' : '27000', 'tempLimit' : '10', 'chargeEndCurrent' : '0.003', 'maxNegDeltaU' : '0.1'}

# litium Ion 16350
LiIon_Cfg = {'curLimit' : '2.0', 'voltLimit' : '4.2', 'timeout' : '11500', 'tempLimit' : '10', 'chargeEndCurrent' : '0.1'}

active_Cfg = NiMH_Cfg

ongoing = True

def cancelProcess():
    global ongoing
    ongoing = False

def isCanceled():
    global ongoing
    return ongoing

def setupSystem():
    usbTemperature.TemperatureInit()
    if False == powerSupply.disableOutput():
        print('ERROR: could not disable Output of Power Supply !')
        sys.exit(1)

def startCharging(config):
    startTemp = usbTemperature.getTemperature()
    config['startTemp'] = startTemp
    config['startTime'] = time.time()
    powerSupply.setCurrentLimit_A(config['curLimit'])
    powerSupply.setVoltage_V(config['voltLimit'])
    powerSupply.enableOutput()

def shallRun(config):
    if False == ongoing:
        return False

    runTime = time.time() - config['startTime']
    print('# run time : %.2f seconds' %(runTime))
    if runTime >  float(config['timeout']):
        return False

    return True

def closeSystem():
    print('Closing down')
    powerSupply.disableOutput()

# main()
setupSystem()
# wait for user to connect the battery
print('Usint this configuration: ')
pprint.pprint(active_Cfg)
input('Connect the Battery and press enter.')
print('stating charge process...')
startCharging(active_Cfg)
temperatureTask = threading.Thread(target=usbTemperature.superviseTemperature, 
args=(active_Cfg, cancelProcess, isCanceled,) )
temperatureTask.start()
powerTask = threading.Thread(target=powerSupply.superviseVoltageAndCurrent,
args=(active_Cfg, cancelProcess, isCanceled, ) )
powerTask.start()

while True == shallRun(active_Cfg):
  time.sleep(1)

#done
cancelProcess() # tell all Threads to shut down
time.sleep(5) # wait for tasks to close
closeSystem()
time.sleep(10)
closeSystem()
print('Battery charging comleted !')
sys.exit(0)

