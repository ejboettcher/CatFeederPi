#!/usr/bin/env python

import time
import sys
import optparse
try:
    import RPi.GPIO as GPIO
except ImportError:
    print "GPIO module for Raspberry Pi not installed!"

class Servo(GPIO.PWM):
    """ 
    basic servo object
    needs a GPIO
    """
    gpioPin = None
    pulseFreq = None
    dutyCycle = None
    
    def __init__(self,gpioPin,pulseFreq,dutyCycle):
        """ 
        gpioPin is the GPIO pin 
        """
        self.gpioPin = gpioPin
        self.pulseFreq = pulseFreq
        self.dutyCycle = dutyCycle

        GPIO.setup(gpioPin,GPIO.OUT)
        
        GPIO.PWM.__init__(self,gpioPin,pulseFreq)

        # no return

    def run(self,onTime):
        self.start(self.dutyCycle)
        time.sleep(onTime)
        self.stop()

if __name__=='__main__':

    parser = optparse.OptionParser()
    parser.addoption('-d','--dry-run',
                     action='store_true',
                     default=False)
    parser.addoption('--donna','--right',
                     action='store_true',
                     default=False)
    parser.addoption('--marilyn','--left',
                     action='store_true',
                     default=False)
    parser.addoption('--both',
                     action='store_true',
                     default=False)
    
    cmdargs,remainder = parser.parse_args()

    # dryrun option selected, exit without running servos
    if cmdargs.d:
        sys.exit(1)
    
    #portionTime = float(sys.argv[1])
    portionTime = float(remainder[0])
    
    GPIO.setmode(GPIO.BCM)

    servo1Pin = 18
    servo2Pin = 23

    pulseFreq = 50.0 # Hertz
    dutyCycle = 10.5 # percent

    # quit for testing
    sys.exit()

    servo1 = Servo(servo1Pin,pulseFreq,dutyCycle)
    servo1.run(portionTime)

    servo2 = Servo(servo2Pin,pulseFreq,dutyCycle)
    servo2.run(portionTime)
    
    GPIO.cleanup()
