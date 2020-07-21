#!/usr/bin/python3
"""
This version is for TMC5160 Chip #2
"""


import logging
import pigpio
import time
import sys
from collections import OrderedDict

import trinamicDriver2, tmc5160regs

class tmc5160():
    def __init__(self, clockfrequ=15000000, stepsPerRev=200, loglvl=logging.DEBUG, vmax=256000, amax=1100, a1=400, dmax=800, d1=300, v1=25000, vstart=10, vstop=20):



        import tmc5160regs

        self.pg=pigpio.pi()
        if not self.pg.connected:
            logging.getLogger().critical("pigpio daemon does not appear to be running")
            sys.exit(1)

        # Define for Motor 3 Blue (Z)
        self.startV=vstart # Inital start velocity in pulses/sec
        self.A1=a1 # Inital acceleration from vstart to v1
        self.V1=v1 # Velocity transition rotation/sec * motorstep * microstep
        self.maxA=amax # Maximum acceleration from vstart to v1
        self.maxV=vmax # Maximum velocity count in rotation/sec * motorstep * microstep
        self.maxD=dmax # Maximum deceleration from vmax to v1
        self.D1=d1 # Final deceleration from v1 to vstop
        self.stopV=vstop # Final stop velocity in pulses/sec




        self.clockfrequ=clockfrequ
        self.uSC=256                 # microsteps per full step 256
        self.stepsPerRev=stepsPerRev # full steps per rev
        self.ustepsPerRev=self.stepsPerRev*self.uSC
        self.uStepsToRPM =  60 * self.clockfrequ / 2**24 / self.ustepsPerRev
        self.md=trinamicDriver2.TrinamicDriver2(clockfrequ=self.clockfrequ, datarate=1000000, pigp=self.pg,
                motordef=tmc5160regs.tmc5160, drvenpin=23, spiChannel=1, loglvl=loglvl )

        regsettings=OrderedDict((
                ('GSTAT',0),
                ('GCONF',0x00000000),
                ('CHOPCONF', 0x000200C3),
                ('IHOLD_IRUN', 0x00080202),
                ('PWMCONF', 0x000401C8),
                ('SWMODE', 0x00000000),
                ('VSTART', self.startV),
                ('A1', self.A1),
                ('V1', self.V1),
                ('AMAX', self.maxA),
                ('VMAX', self.maxV),
                ('DMAX', self.maxD),
                ('D1', self.D1 ),
                ('VSTOP', self.stopV),
               # ('V2START', self.start2V),
               # ('A21', self.A21),
               # ('V21', self.V21),
               # ('A2MAX', self.max2A),
               # ('V2MAX', self.max2V),
               # ('D2MAX', self.max2D),
               # ('D21', self.D21 ),
               # ('V2STOP', self.stop2V),
               # ('CHOPCONF2', 0x000100C3),
               # ('PWMCONF2', 0x000401C8),
               # ('IHOLD_IRUN2', 0x00080F0A),
               # ('SWMODE2', 0x00000000),
                ('RAMPMODE',0),
                # ('RAMPMODE2',0)
                 ))
        regactions='RUWWWWWWWWWWWWW'
        assert len(regsettings)==len(regactions)
        currently=self.md.readWriteMultiple(regsettings,regactions)

    ################################################################################################
    ############################## Routines for TMC5072 #2 1st Motor  #################################
    ################################################################################################


    def wait_reached(self, ticktime=.5):
        time.sleep(ticktime)
        reads={'VACTUAL':0, 'XACTUAL':0, 'XTARGET':0, 'GSTAT':0, 'RAMPSTAT':0,'V2ACTUAL':0, 'X2ACTUAL':0, 'X2TARGET':0,'RAMPSTAT2':0,}
        self.md.readWriteMultiple(reads, 'R')
        while self.md.readInt('XACTUAL') != self.md.readInt('XTARGET'):
            time.sleep(ticktime)
            self.md.readWriteMultiple(reads, 'R')

    def waitStop(self, ticktime):
        time.sleep(ticktime)
        while self.md.readInt('VACTUAL') != 0:
            time.sleep(ticktime)

    def zgoto(self, targetpos, wait=True):
        self.md.enableOutput(True)
        self.md.writeInt('XTARGET',int(targetpos))
        if wait:
            self.wait_reached()

    def zgotonowait(self, targetpos, wait=True):
        self.md.enableOutput(True)
        self.md.writeInt('XTARGET',int(targetpos))


    def zhome(self, homepos, wait=True):
        self.md.writeInt('VMAX', 90000)
        self.md.enableOutput(True)
        self.md.writeInt('XTARGET',int(homepos))
        time.sleep(0.1)
        while self.md.readInt('VACTUAL') != 0:
            time.sleep(0.01)
        #print('Actual Position =', self.md.readInt('XACTUAL') )
        reads={'VACTUAL':0, 'XACTUAL':0, 'XTARGET':0, 'GSTAT':0, 'RAMPSTAT':0}
        self.md.readWriteMultiple(reads, 'R')
        limittest=reads['RAMPSTAT']
        #print('***** Limit Test *****', limittest)
        self.md.writeInt('VMAX', 40000)
        self.md.writeInt('XTARGET', 5000)
        time.sleep(0.01)
        while reads['RAMPSTAT'] <= 2:
            self.md.writeInt('XTARGET', 5000)
            limittest=reads['RAMPSTAT']
            #print('***** Limit Test *****', limittest)
            time.sleep(0.01)
            self.md.readWriteMultiple(reads, 'R')
        self.md.writeInt('XTARGET', self.md.readInt('XACTUAL'))
        rstat=', '.join(self.md.flagsToText(reads['RAMPSTAT'], 'rampstatBits'))
        self.md.writeInt('XTARGET', self.ustepsPerRev + self.md.readInt('XACTUAL') )
        if wait:
            self.wait_reached()
        #print('Home Reached, Actual Position = ', reads['XACTUAL'])
        self.md.writeInt('VMAX', self.maxV)

    def zenergize(self, wait=True):
        self.md.enableOutput(True)

    def zsoftenergize(self, wait=True):
        self.md.writeInt('IHOLD_IRUN', 0x00080202)
        time.sleep (0.3)
        self.md.writeInt('IHOLD_IRUN', 0x00080606)
        time.sleep (0.3)
        self.md.writeInt('IHOLD_IRUN', 0x00080A0A)
        time.sleep (0.3)
        self.md.writeInt('IHOLD_IRUN', 0x00080F0A)
        self.md.enableOutput(True)

    def zmotorcurrent(self, zihold, zirun, zihdelay, wait=True):
        zihold = int(zihold)
        zirun = int(zirun) * 16**2
        zihdelay = int(zihdelay) * 16**4
        zmotorcurrent = int(zihold + zirun + zihdelay)
        self.md.writeInt('IHOLD_IRUN',zmotorcurrent)
        self.md.enableOutput(True)

    def zdenergize(self, wait=True):
        self.md.enableOutput(False)

    def zstop(self):
        self.md.writeInt('XTARGET', self.md.readInt('XACTUAL'))
        self.md.writeInt('VMAX', self.maxV)
        self.md.writeInt('RAMPMODE',0)
        self.waitStop(ticktime=.1)
        self.md.enableOutput(False)


    ################################################################################################
    ############################ Routines for both TMC5072 #2 Motors ##################################
    ################################################################################################

    def zclose(self):
        self.md.enableOutput(True)
        self.md.close()


