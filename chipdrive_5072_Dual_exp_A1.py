#!/usr/bin/python3
"""

This version is for TMC5072 Chip
Driver for a trinamic tmc5072-bob on a raspberry pi using SPI based from pootle.
https://github.com/pootle/tripipy

"""


import logging
import pigpio
import time
import sys
from collections import OrderedDict

import trinamicDriver, tmc5072regs

class tmc5072():
    def __init__(self, clockfrequ=15000000, stepsPerRev=400, loglvl=logging.DEBUG, vmax=512000, amax=2200, a1=800, dmax=1700, d1=600, v1=25000, vstart=1, vstop=2, v2max=512000, a2max=2200, a21=800, d2max=1700, d21=600, v21=25000, v2start=1, v2stop=2):

        """
        sets up a motor driver for the trinamic tmc5072

        clockfrequ   : clock frequency (generated by the RPi and passed to the chip, 10MHz - 16MHz recommended in manual

        stepsPerRev  : Defined by the motor - number of full steps per rev, 200 for NEMA 11 with THK KR15 Rail or 400 for NEMA 17 with THK KR20 or HIWIN.
        """

        import tmc5072regs

        self.pg=pigpio.pi()
        if not self.pg.connected:
            logging.getLogger().critical("pigpio daemon does not appear to be running")
            sys.exit(1)

        # Define for Motor 1 Purple (X)
        self.startV=vstart # Inital start velocity in pulses/sec
        self.A1=a1 # Inital acceleration from vstart to v1
        self.V1=v1 # Velocity transition rotation/sec * motorstep * microstep
        self.maxA=amax # Maximum acceleration from vstart to v1
        self.maxV=vmax # Maximum velocity count in rotation/sec * motorstep * microstep
        self.maxD=dmax # Maximum deceleration from vmax to v1
        self.D1=d1 # Final deceleration from v1 to vstop
        self.stopV=vstop # Final stop velocity in pulses/sec

        # Define for Motor 2 Green (Y)
        self.start2V=v2start # Inital start velocity in pulses/sec
        self.A21=a21 # Inital acceleration from vstart to v1
        self.V21=v21 # Velocity transition rotation/sec * motorstep * microstep
        self.max2A=a2max # Maximum acceleration from vstart to v1
        self.max2V=v2max # Maximum velocity count in rotation/sec * motorstep * microstep
        self.max2D=d2max # Maximum deceleration from vmax to v1
        self.D21=d21 # Final deceleration from v1 to vstop
        self.stop2V=v2stop # Final stop velocity in pulses/sec




        self.clockfrequ=clockfrequ
        self.uSC=256                 # microsteps per full step 256
        self.stepsPerRev=stepsPerRev # full steps per rev
        self.ustepsPerRev=self.stepsPerRev*self.uSC
        self.uStepsToRPM =  60 * self.clockfrequ / 2**24 / self.ustepsPerRev
        self.md=trinamicDriver.TrinamicDriver(clockfrequ=self.clockfrequ, datarate=1000000, pigp=self.pg,
                motordef=tmc5072regs.tmc5072, drvenpin=12, spiChannel=0, loglvl=loglvl )

        regsettings=OrderedDict((
                ('GSTAT',0),
                ('GCONF',0x00000000),
                ('CHOPCONF', 0x00030043), # Vsense =1; TBL=10 CHM=0 (Spreadcycle)
                ('IHOLD_IRUN', 0x00080200),
                ('TCOOLTHRS', 0x00061A0),
                ('THIGH', 0x00061A0),
                ('PWMCONF', 0x000701FF),
                ('SWMODE', 0x00000000),
                ('VSTART', self.startV),
                ('A1', self.A1),
                ('V1', self.V1),
                ('AMAX', self.maxA),
                ('VMAX', self.maxV),
                ('DMAX', self.maxD),
                ('D1', self.D1 ),
                ('VSTOP', self.stopV),
                ('V2START', self.start2V),
                ('A21', self.A21),
                ('V21', self.V21),
                ('A2MAX', self.max2A),
                ('V2MAX', self.max2V),
                ('D2MAX', self.max2D),
                ('D21', self.D21 ),
                ('V2STOP', self.stop2V),
                ('CHOPCONF2', 0x00030043),
                ('PWMCONF2', 0x000701FF),
                ('IHOLD_IRUN2', 0x00080200),
                ('T2COOLTHRS', 0x00061A0),
                ('T2HIGH', 0x00061A0),
                ('SWMODE2', 0x00000000),
                ('RAMPMODE',0),
                ('RAMPMODE2',0)
                 ))
        regactions='RUWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW'
        assert len(regsettings)==len(regactions)
        currently=self.md.readWriteMultiple(regsettings,regactions)

    ################################################################################################
    ############################## Routines for TMC5072 #1 1st Motor  #################################
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

    def xgoto(self, targetpos, wait=True):
        self.md.enableOutput(True)
        self.md.writeInt('XTARGET',int(targetpos))
        if wait:
            self.wait_reached()

    def xgotonowait(self, targetpos, wait=True):
        self.md.enableOutput(True)
        self.md.writeInt('XTARGET',int(targetpos))


    def xhome(self, homepos, wait=True):
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

    def xenergize(self, wait=True):
        self.md.writeInt('IHOLD_IRUN', 0x00080F0A)
        self.md.enableOutput(True)

    def xsoftenergize(self, wait=True):
        self.md.writeInt('IHOLD_IRUN', 0x00080202)
        time.sleep (0.3)
        self.md.writeInt('IHOLD_IRUN', 0x00080606)
        time.sleep (0.3)
        self.md.writeInt('IHOLD_IRUN', 0x00080A0A)
        time.sleep (0.3)
        self.md.writeInt('IHOLD_IRUN', 0x00080F0A)
        self.md.enableOutput(True)

    def xmotorcurrent(self, xihold, xirun, xihdelay, wait=True):
        xihold = int(xihold)
        xirun = int(xirun) * 16**2
        xihdelay = int(xihdelay) * 16**4
        xmotorcurrent = int(xihold + xirun + xihdelay)
        self.md.writeInt('IHOLD_IRUN',xmotorcurrent)
        self.md.enableOutput(True)

    def xdenergize(self, wait=True):
        self.md.enableOutput(False)

    def xstop(self):
        self.md.writeInt('XTARGET', self.md.readInt('XACTUAL'))
        self.md.writeInt('VMAX', self.maxV)
        self.md.writeInt('RAMPMODE',0)
        self.waitStop(ticktime=.1)
        self.md.enableOutput(False)

    ################################################################################################
    ################################ Routines for TMC5072 #1 2nd Motor ################################
    ################################################################################################

    def wait_reached2(self, ticktime=.5):
        time.sleep(ticktime)
        reads={'VACTUAL':0, 'XACTUAL':0, 'XTARGET':0, 'GSTAT':0, 'RAMPSTAT':0,'V2ACTUAL':0, 'X2ACTUAL':0, 'X2TARGET':0,'RAMPSTAT2':0,}
        self.md.readWriteMultiple(reads, 'R')
        while self.md.readInt('X2ACTUAL') != self.md.readInt('X2TARGET'):
            time.sleep(ticktime)
            self.md.readWriteMultiple(reads, 'R')

    def waitStop2(self, ticktime):
        time.sleep(ticktime)
        while self.md.readInt('V2ACTUAL') != 0:
            time.sleep(ticktime)

    def ygoto2(self, targetpos, wait=True):
        self.md.enableOutput(True)
        self.md.writeInt('X2TARGET',int(targetpos))
        if wait:
            self.wait_reached2()

    def ygotonowait2(self, targetpos, wait=True):
        self.md.enableOutput(True)
        self.md.writeInt('X2TARGET',int(targetpos))

    def yenergize2(self, wait=True):
        self.md.writeInt('IHOLD_IRUN2', 0x00080F0A)
        self.md.enableOutput(True)

    def ysoftenergize2(self, wait=True):
        self.md.writeInt('IHOLD_IRUN2', 0x00080202)
        time.sleep (0.3)
        self.md.writeInt('IHOLD_IRUN2', 0x00080606)
        time.sleep (0.3)
        self.md.writeInt('IHOLD_IRUN2', 0x00080A0A)
        time.sleep (0.3)
        self.md.writeInt('IHOLD_IRUN2', 0x00080F0A)
        self.md.enableOutput(True)

    def ymotorcurrent2(self, yihold, yirun, yihdelay, wait=True):
        yihold = int(yihold)
        yirun = int(yirun) * 16**2
        yihdelay = int(yihdelay) * 16**4
        ymotorcurrent2 = int(yihold + yirun + yihdelay)
        self.md.writeInt('IHOLD_IRUN2',ymotorcurrent2)
        self.md.enableOutput(True)


    def ydenergize2(self, wait=True):
        self.md.enableOutput(False)


    def ystop2(self):
        self.md.writeInt('X2TARGET', self.md.readInt('X2ACTUAL'))
        self.md.writeInt('V2MAX', self.max2V)
        self.md.writeInt('RAMPMODE2',0)
        self.waitStop2(ticktime=.1)
        self.md.enableOutput(False)

    ################################################################################################
    ############################ Routines for both TMC5072 #1 Motors ##################################
    ################################################################################################

    def xclose(self):
        self.md.enableOutput(True)
        self.md.close()



