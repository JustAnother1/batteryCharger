#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import os
import time
import re

#./sigrok-cli  --driver korad-kaxxxxp:conn=/dev/ttyACM0 --config "enabled=off" --set
#./sigrok-cli  --driver korad-kaxxxxp:conn=/dev/ttyACM0  --get enabled
#false
def disableOutput():
    my_env = os.environ.copy()
    my_env["LD_LIBRARY_PATH"] = os.getcwd() + '/sr/lib'
    print('# disable output')
    proc = subprocess.run(['./sr/bin/sigrok-cli', '--driver', 'korad-kaxxxxp:conn=/dev/ttyACM0', '--config',  'enabled=off', '--set'], env=my_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    print('# check that output is disabled')
    proc = subprocess.run(['./sr/bin/sigrok-cli', '--driver', 'korad-kaxxxxp:conn=/dev/ttyACM0', '--get',  'enabled'], stdout=subprocess.PIPE, env=my_env, stderr=subprocess.DEVNULL)
    res = proc.stdout.decode("utf-8")
    #print('# res :  _' + res + '_ !')
    if 'false\n' == res:
        return True
    else:
        return False


def enableOutput():
    print('# enable output')
    my_env = os.environ.copy()
    my_env["LD_LIBRARY_PATH"] = os.getcwd() + '/sr/lib'
    proc = subprocess.run(['./sr/bin/sigrok-cli', '--driver', 'korad-kaxxxxp:conn=/dev/ttyACM0', '--config', 'enabled=on', '--set'], env=my_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def setCurrentLimit_A(value):
    print('# set current limit to %.3f A' % (float(value)))
    my_env = os.environ.copy()
    my_env["LD_LIBRARY_PATH"] = os.getcwd() + '/sr/lib'
    proc = subprocess.run(['./sr/bin/sigrok-cli', '--driver', 'korad-kaxxxxp:conn=/dev/ttyACM0', '--config', 'current_limit=' + value, '--set'], env=my_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def setVoltage_V(value):
    print('# set Voltage to %.3f V' % (float(value)))
    my_env = os.environ.copy()
    my_env["LD_LIBRARY_PATH"] = os.getcwd() + '/sr/lib'
    proc = subprocess.run(['./sr/bin/sigrok-cli', '--driver', 'korad-kaxxxxp:conn=/dev/ttyACM0', '--config', 'voltage_target=' + value, '--set'], env=my_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def superviseVoltageAndCurrent(cfg ,cancel, run):
    minI = float(cfg['chargeEndCurrent']) * 1000  # convert A to mA
    maxU = 0.0
    if 'maxNegDeltaU' in cfg.values():    
        maxNegDeltaU = cfg['maxNegDeltaU']
    else:
        maxNegDeltaU = 100.0 # basically I don't care
    print('# enable output')
    CurrentRegEx = re.compile(r'I: \d+ mA')
    VoltageRegEx = re.compile(r'V: \d+\.\d+ V DC')
    numberRegEx = re.compile(r'\d+')
    floatRegEx = re.compile(r'\d+\.\d+')
    my_env = os.environ.copy()
    my_env["LD_LIBRARY_PATH"] = os.getcwd() + '/sr/lib'
    proc = subprocess.Popen(['./sr/bin/sigrok-cli', '--driver', 'korad-kaxxxxp:conn=/dev/ttyACM0', '--continuous'], stdout=subprocess.PIPE, env=my_env, universal_newlines=True, stderr=subprocess.DEVNULL)

    logFile = open('energy_log.csv', 'w')
    logFile.write('time in seconds, current in A,\n')
    while True == run():
        line = proc.stdout.readline()
        
        # current
        ok = CurrentRegEx.search(line)
        if None != ok:
            # this line contains a current
            res = line.split()
            for part in res:
                match = numberRegEx.search(part)
                if None != match:
                     current = float(part)
                     runTime = time.time() - cfg['startTime']
                     logFile.write('%.2f, %.2f,\n' % (runTime, current))
                     print('# current: %.2f mA' % (current))
                     if float(minI) > current:
                         print('current dropped to ' + str(current) + ' mA -> stopping charge!')
                         cancel()
                         logFile.close()
                         return
                         
        # voltage
        ok = VoltageRegEx.search(line)
        if None != ok:
            # this line contains a voltage
            res = line.split()
            for part in res:
                match = floatRegEx.search(part)
                if None != match:
                     voltage = float(part)
                     runTime = time.time() - cfg['startTime']
                     logFile.write('%.2f, %.2f,\n' % (runTime, voltage))
                     print('# voltage: %.2f V' % (voltage))
                     if maxU < voltage:
                         maxU = voltage
                     if voltage < maxU:
                         deltaU = maxU - voltage
                         if deltaU > maxNegDeltaU:
                             print('voltage dropped to ' + str(voltage) + ' V  (max was : ' + str(maxU) + ')-> stopping charge!')
                             cancel()
                             logFile.close()
                             return

    proc.terminate()
    logFile.close()
    time.sleep(1)
    if None == proc.returncode:
        proc.kill()



##main
#disableOutput()

