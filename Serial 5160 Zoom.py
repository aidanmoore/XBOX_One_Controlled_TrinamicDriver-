########### Aidan Moore XBox Control of Trinamic Motor Drivers
# July 21 2020
#This version is first GIT commit for TMC5072, TMC5160 and TMC2208 for zoom motor
# Now with Serial commands to Arduino Uno to control a Brightfield/Darkfield LED light
# With Raspberry Pi 4
# Motor Supply 12 Volts or Greater
# Uses XBOX One Bluetooth controller to move XY motors adjust Z focus, control a zoom stepper motor and control the Arduino LED driver 

# Uses SPI to send and receive data from Raspberry Pi, (0) for TMC5072 #1 (ENN GPIO 12 {pin 32}) and (1) for TMC5160 #2 (ENN GPIO 21 {pin 40})
#     Works with Python 3
#
# Run sudo pigpiod before starting program (in batch file)
# This is part of bashrc ie nano ~/ .bashrc
#   alias python='/usr/bin/python3'
# alias pip=pip3
#  sudo pigpiod
# run as :  sudo python3 1axis_rawPLAY.py
#
#
#     

# Import Libraries
from __future__ import print_function
import time
import pigpio
import chipdrive_5072_Dual_exp_A1, chipdrive_5160_Dual_exp_A2 # This is Trinamic chipdrive for Dual TMC5072 Chips 1 and TMC5160 
import trinamicDriver, trinamicDriver2, tmc5072regs, tmc5160regs
import sys
import serial

# Instantiate the USB Serial port connection to the Arduino

arduino =serial.Serial('/dev/ttyACM0', 9600)

# Connect to pigpiod daemon to control GPIO
pi = pigpio.pi()

# Instantiate the XBOX BT controller (XBOX ONE)
import gamepad2 #this is an updated version with all buttons mapped
import asyncio # asyncio is needed to use the Bluetooth version of the XBOX controller
import evdev #import InputDevice, ff, ecodes
joy = gamepad2.gamepad

# Set Raspberry ports for Trinamic 5160 and 5072 motor controllers
motorport1 = 12 # Motor GPIO enable port number 12 for driver #1 on Raspberry Pi 3
motorport2 = 23 # Motor GPIO enable port number 23 for 5160 driver #2 on Raspberry Pi 3
pi.set_mode(motorport1, pigpio.OUTPUT) # Set driver chip #1 port to output
pi.set_mode(motorport2, pigpio.OUTPUT) # Set driver chip #2 port to output
pi.write(motorport1, 1) # Set motor port initally to 1 to disable
pi.write(motorport2, 1) # Set motor port initally to 1 to disable

# Zoom motor settings for Trinamic TMC2208 interface
zoomstep = 14 # Step control for zoom stepper motor on TMC2208
zoomdir = 13  # Direction Control for zoom stepper motor on TMC2208
zoomena = 6   # Enable for zoom stepper motor on TMC2208
zoomms1 = 3   # Microstep input MS1 for zoom stepper motor on TMC2208
zoomms2 = 5   # Microstep input MS1  for zoom stepper motor on TMC2208

# Set up Zoom motor pins as outputs

pi.set_mode(zoomdir, pigpio.OUTPUT)
pi.set_mode(zoomstep, pigpio.OUTPUT)
pi.set_mode(zoomena, pigpio.OUTPUT)
pi.set_mode(zoomms1, pigpio.OUTPUT)
pi.set_mode(zoomms2, pigpio.OUTPUT)


################################################### For TMC5072 #1 ######################################################

# Number 1 Motor X (Purple Dot Motor #1 on PCB) and Rail Setup Parameters
# Controller is Trinamic #1 TMC-5072 SPI (0) ENN GPIO 12
xmotorstep = 400 # Motor steps per rotation
xvmax = 256000 # Maximum velocity count in rotation/sec vmax/motorstep/microstep
xamax = 1100 # Maximum acceleration from v1 to vmax
xa1 = 200 # Maximum acceleration from vstart to v1
xdmax = 800 # Maximum deceleration from vmax to v1
xd1 = 300 # Final deceleration from v1 to vstop
xv1 = 250000 # Velocity transition rotation/sec v1/motorstep/microstep
xvstart = 10 # Inital start velocity in pulses/sec
xvstop = 20 # Final stop velocity in pulses/sec, Note must be > than vstart!

# Number 2 Y (Green Dot Motor #2 on PCB) Motor and Rail Setup Parameters
# Controller is Trinamic #1 TMC-5072 SPI (0) ENN GPIO 12
ymotorstep2 = 400 # Motor steps per rotation
y2vmax = 256000 # Maximum velocity count in rotation/sec vmax/motorstep/microstep
y2amax = 1100 # Maximum acceleration from v1 to vmax
y2a1 = 200 # Maximum acceleration from vstart to v1
y2dmax = 800 # Maximum deceleration from vmax to v1
y2d1 = 300 # Final deceleration from v1 to vstop
y2v1 = 250000 # Velocity transition rotation/sec v1/motorstep/microstep
y2vstart = 10 # Inital start velocity in pulses/sec
y2vstop = 20 # Final stop velocity in pulses/sec, Note must be > than vstart!

# Read in data from Trinimac Specific Controller
# Note this is tmc5072 #1 define as "mot1"
md1=trinamicDriver.TrinamicDriver(datarate=1000000, motordef=tmc5072regs.tmc5072, drvenpin=12, spiChannel=0) # Setup md for reading position
mot1=chipdrive_5072_Dual_exp_A1.tmc5072(stepsPerRev=xmotorstep, vmax=xvmax, amax=xamax, a1=xa1, dmax=xdmax, d1=xd1, v1=xv1, vstart=xvstart, vstop=xvstop, v2max=y2vmax, a2max=y2amax, a21=y2a1, d2max=y2dmax, d21=y2d1, v21=y2v1, v2start=y2vstart, v2stop=y2vstop) # Activate Chip Drive for TMC5072 as mot1

################################################### For TMC5160 #2 ######################################################

zmotorstep = 200 # Motor steps per rotation
zvmax = 256000 # Maximum velocity count in rotation/sec vmax/motorstep/microstep
zamax = 1100 # Maximum acceleration from v1 to vmax
za1 = 400 # Maximum acceleration from vstart to v1
zdmax = 800 # Maximum deceleration from vmax to v1
zd1 = 300 # Final deceleration from v1 to vstop
zv1 = 25000 # Velocity transition rotation/sec v1/motorstep/microstep
zvstart = 10 # Inital start velocity in pulses/sec
zvstop = 20 # Final stop velocity in pulses/sec, Note must be > than vstart!

# Read in data from Trinimac Specific Controller
# Note this is tmc5160 #2 define as "mot2"
md2=trinamicDriver2.TrinamicDriver2(datarate=1000000, motordef=tmc5160regs.tmc5160, drvenpin=23, spiChannel=1) # Setup md for reading position
mot2=chipdrive_5160_Dual_exp_A2.tmc5160(stepsPerRev=zmotorstep, vmax=zvmax, amax=zamax, a1=za1, dmax=zdmax, d1=zd1, v1=zv1, vstart=zvstart, vstop=zvstop) # Activate Chip Drive for TMC5072 as mot2

################################################### Setup Critical Currents for Trinamic Controllers ######################################################

# Set Motor 1 Default Currents and Irun to Ihold Delay 
xihold = 2 # R motor hold current imax*(ihold + 1)/32
xirun = 10 # R motor run current imax*(irun + 1)/32
xihdelay = 4 # R motor hold delay (irun-ihold)*ihdelay*2^18/fclock
mot1.xmotorcurrent(xihold, xirun, xihdelay) # Write motor currents and hold delay


# Set Motor 2 Default Currents and Irun to Ihold Delay 
yihold2 = 2 # R motor hold current imax*(ihold + 1)/32
yirun2 = 10 # R motor run current imax*(irun + 1)/32
yihdelay2 = 4 # R motor hold delay (irun-ihold)*ihdelay*2^18/fclock
mot1.ymotorcurrent2(yihold2, yirun2, yihdelay2) # Write motor currents and hold delay


time.sleep(1.5) # this prevents an unknown inrush current on TMC5160
# Set Motor 3 Default Currents and Irun to Ihold Delay 
zihold = 2 # R motor hold current imax*(ihold + 1)/32
zirun = 8 # R motor run current imax*(irun + 1)/32
zihdelay = 8 # R motor hold delay (irun-ihold)*ihdelay*2^18/fclock
mot2.zmotorcurrent(zihold, zirun, zihdelay) # Write motor currents and hold delay

mot1.xdenergize() # Denergize Motor 1 TMC5072 Chip #1
mot1.ydenergize2() # Denergize Motor 2 TMC5072 Chip #1
mot2.zdenergize() # Denergize Motor 1 TMC5160 Chip #1 disabled due to jerk

################################################### Main Routine ######################################################

try:
    async def main():
        
        XFLAG = 0 # 1 = deenergized and target reached 0 = target not reached
        YFLAG = 0 # 1 = deenergized and target reached 0 = target not reached
        ZFLAG = 0
        XNOW = 0 # 1 = deenergized and target reached 0 = target not reached
        YNOW = 0 # 1 = deenergized and target reached 0 = target not reached
        ZNOW = 0
        XPOS = md1.readInt('XACTUAL')
        YPOS = md1.readInt('X2ACTUAL')
        ZPOS = md2.readInt('XACTUAL')
        LEDANGLE = 0
        XSCALE = 20
        YSCALE = 20
        ZSCALE = 2 #start in fine mode
        pi.write(zoomdir, 0)  #zoom direction is zero
        pi.write (zoomstep,0) #zoom step is zero
        pi.write (zoomena,1) #zoom motor is disabled
        pi.write (zoomms1,1) #zoom speed is slowest
        pi.write (zoomms2,1) 
        keep_going = True
 
 ################################################### Main Loop ######################################################

        while keep_going:
            
            XNOW = round(remote_control.joystick_left_x,4) #Read Left X Joystick to get THK26 X axis next position
            YNOW = round(remote_control.joystick_left_y,4) #Read Left Y Joystick to get THK26 Y axis next position
            ZNOW = round(remote_control.joystick_right_y,4)#Read Right Y Joystick to get THK Z (focus) axis next position
            ZOOMIN = remote_control.trigger_left           #Read Left trigger (LT) to get THK26 X axis next position (0 -1023)
            ZOOMOUT = remote_control.trigger_right         #Read RIGHT trigger (rT) to get THK26 y axis next position (0 - 1023)

    
            ####### Check if a new joystick value was read and go there if a new value found #######
            
            if  abs(XNOW) >0.1:  # if the Joystick is not in deadband  
                XPOS = XPOS + XSCALE * XNOW #Change the target
                mot1.xgotonowait(XPOS) # Write position count to Trinamic 5072 #1 Motor 1(Purple)
                XFLAG = 1
            if  abs(YNOW) > 0.1:
                YPOS = YPOS + YSCALE * YNOW
                mot1.ygotonowait2(YPOS) # Write position count to Trinamic 5072 #1 Motor 2 (Green)
                YFLAG = 1
            if abs(ZNOW) > 0.1:
                ZPOS = ZPOS + ZSCALE * ZNOW
                mot2.zgotonowait(ZPOS) # Write position count to Trinamic 5160 Motor 3
                ZFLAG = 1
                
            ####### Check ZOOMIN trigger value and set microstep (speed) value then set direction and pulse motor #######
             
            if (ZOOMIN) > 50:  #If the XBOX Left trigger control is not in the deadband or zero
                 
                if 1024 > (ZOOMIN) > 750 : #fastest 1/2
                        pi.write (zoomms1,1)
                        pi.write (zoomms2, 0)                  
                if 749 > (ZOOMIN) > 500 : #2nd fastest 1/4
                        pi.write (zoomms1,0)
                        pi.write (zoomms2, 1)                       
                if 499 > (ZOOMIN) > 250 : # 2nd slowest 1/8
                        pi.write (zoomms1,0)
                        pi.write (zoomms2, 0)                      
                if 249 > (ZOOMIN) > 50 :  # 2nd slowest 1/16
                        pi.write (zoomms1,1)
                        pi.write (zoomms2, 1)                   
                pi.write (zoomena,0) #zoom motor enabled
                pi.write(zoomdir, 1) #set direction
                pi.write (zoomstep,1) #pulse
                await asyncio.sleep(0.001)
                pi.write (zoomstep,0)
                
            ####### Check ZOOMOUT trigger value and set microstep (speed) value then set direction and pulse motor #######              

            if (ZOOMOUT) > 50:        #If the XBOX Right trigger control is not in the deadband or zero
                if 1024 > (ZOOMOUT) > 750 : #fastest 1/2
                        pi.write (zoomms1,1)
                        pi.write (zoomms2, 0)
                if 749 > (ZOOMOUT) > 500 : #2nd fastest 1/4
                        pi.write (zoomms1,0)
                        pi.write (zoomms2, 1)
                if 499 > (ZOOMOUT) > 250 : #1/8
                        pi.write (zoomms1,0)
                        pi.write (zoomms2, 0)
                if 249 > (ZOOMOUT) > 50 :
                        pi.write (zoomms1,1)
                        pi.write (zoomms2, 1)
                pi.write (zoomena,0) #zoom motor enabled
                pi.write(zoomdir, 0) #set direction
                pi.write (zoomstep,1) #pulse
                await asyncio.sleep(0.001)
                pi.write (zoomstep,0)
      
    #
    # Now test if the THK KR motors have arrived at the target position. If they have, deenergize the motor.
    #   
            if md1.readInt('XACTUAL') == md1.readInt('XTARGET') and XFLAG == 1 : # if the target is reached and the flag is set  
                XFLAG = 0         # Clear the flag
                mot1.xdenergize() # Denergize Motor 1 TMC5072 Chip #1
                print (' X target reached ')   
            if md1.readInt('X2ACTUAL') == md1.readInt('X2TARGET') and YFLAG == 1 : # if the target is reached and the flag is set  
                YFLAG = 0         # Clear the flag
                mot1.ydenergize2() # Denergize Motor 2 TMC5072 Chip #1        
                print (' Y target reached ')
            if md2.readInt('XACTUAL') == md2.readInt('XTARGET') and ZFLAG == 1 : # if the target is reached and the flag is set  
                ZFLAG = 0         # Clear the flag
                # mot2.zdenergize() # Denergize Motor 1 TMC5160 Chip #1 But getting jerk so disabled       
                print (' Z target reached ')

    #
    # Read the XBOX Controller Buttons
    #
            if remote_control.button_x: # Super fine mode resolution for XYZ THK rails
                remote_control.button_x = False
                ZSCALE = 2 #super fine mode
                XSCALE = 10 #super fine mode
                YSCALE = 10 #super fine mode
                print ("Super Fine Mode")
             
            if remote_control.button_y: # Fine mode resolution for XYZ THK rails
                remote_control.button_y = False
                ZSCALE = 6 #fine mode
                XSCALE = 30 #fine mode
                YSCALE = 30 #fine mode                   
                print ("Fine Mode")
     
            if remote_control.button_b: #Coarse mode resolution for XYZ THK rails
                remote_control.button_b = False
                ZSCALE = 12 #coarse mode
                XSCALE = 60 #coarse mode
                YSCALE = 60 #coarse mode
                print ("Coarse Mode")
                remote_control.rumble_effect = 2  # play once strong rumble effect
                
            if remote_control.button_a: #Super Coarse mode resolution for XYZ THK rails
                remote_control.button_a = False
                ZSCALE = 54 #coarse mode
                XSCALE = 120 #super coarse mode
                YSCALE = 120 #super coarse mode
                print (" Super Coarse Mode")
                remote_control.rumble_effect = 2   # play once strong rumble effect          
                 
            if remote_control.button_rb: # Toggle Arduino Darkfield on and off
                remote_control.button_rb = False
                sm = 'r'
                arduino.write(sm.encode())
                print ("Toggle Darkfield")
                
            if remote_control.button_lb: #Toggle Arduino Brightfield on and off
                remote_control.button_lb = False
                sm = 'e'
                arduino.write(sm.encode())
                print ("Toggle Brightfield")
                
            if remote_control.dpad_x == 1 : #Increment Arduino Angle
                remote_control.dpad_x = 0 
                sm = 'd'
                arduino.write(sm.encode())
                print ("Increment LED Angle")
                
            if remote_control.dpad_x == -1: #Decrement Arduino Angle
                remote_control.dpad_x = 0
                sm = 'a'
                arduino.write(sm.encode())
                print ("Decrement LED Angle")
                
            if remote_control.dpad_y == 1 : #Increment Arduino Mode
                remote_control.dpad_y = 0 
                sm = 'w'
                arduino.write(sm.encode())
                print ("Increment LED Mode")
                
            if remote_control.dpad_y == -1: #Increment Arduino Angle
                remote_control.dpad_y = 0
                sm = 's'
                arduino.write(sm.encode())
                print ("Decrement LED Mode")                   
                    
            if remote_control.button_back: # Exit program
                remote_control.button_back = False
                print ("Goodbye")
                sys.exit()

            ### Zoom motor is still enabled at this point to allow smooth step operation. Disable zoom motor here. 
            pi.write (zoomena,1) #zoom motor disabled
            ZOOMIN = 0
            ZOOMOUT = 0
            await asyncio.sleep(0)       

    remote_control = joy(file = '/dev/input/event0')
    futures = [remote_control.read_gamepad_input(), remote_control.rumble(), main()]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(futures))
    loop.close()

except: 
    mot2.zdenergize() # Denergize Motor 1 TMC5160 Chip #1
    mot1.ydenergize2() # Denergize Motor 2 TMC5072 Chip #1
    mot1.xdenergize() # Denergize Motor 1 TMC5072 Chip #1
    pi.write (zoomena,1) #zoom motor disabled
    pi.stop() #close gpio
    print ("Exit Routine!")
    
