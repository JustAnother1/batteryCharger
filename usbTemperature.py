#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import time

# install:
#sudo apt-get install digitemp
#digitemp_DS9097 -i -s /dev/ttyUSB0

# execute
#$ digitemp_DS9097 -q -t 0
#Jan 21 17:12:33 Sensor 0 C: 20.94 F: 69.69


def TemperatureInit():
    if False ==  os.path.isfile('.digitemprc'):
        proc = subprocess.run(["digitemp_DS9097", "-i", "-s", "/dev/ttyUSB0"])


def getTemperature():
    proc = subprocess.run(["digitemp_DS9097", "-q", "-t", "0"], stdout=subprocess.PIPE)
    res = proc.stdout.decode("utf-8")
    resParts = res.split()
    temperature = resParts[6]
    return float(temperature)

def superviseTemperature(cfg, cancel, run):
    logFile = open('temperature_log.csv', 'w')
    logFile.write('time in seconds, temperature in degree C,\n')
    ref = cfg['startTemp']
    maxDeviation = cfg['tempLimit']
    while True == run():
        curTemp = getTemperature() 
        runTime = time.time() - cfg['startTime']
        logFile.write('%.2f, %.2f,\n' % (runTime, curTemp))
        print("# Temperature : %.2f °C" % (curTemp))     
        if curTemp > float(ref) + float(maxDeviation):
            print('ERROR: Temperature too High !')
            cancel()
            logFile.close()
            return
        if curTemp < float(ref) - float(maxDeviation):
            print('ERROR: Temperature too low !')
            cancel()
            logFile.close()
            return

    logFile.close()

def cancelCB():
    print('Cancel got called !')
    sys.exit(1)

##main()
#TemperatureInit()
#temperature = getTemperature()
#print("# Temperature : %s °C" % (temperature))
##superviseTemperature(temperature, 3, cancelCB)




