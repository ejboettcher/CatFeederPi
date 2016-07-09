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
    parser.add_option('-v','--verbose',
                      action='store_true',
                      default=False,
                      help='turn on verbosity')
    parser.add_option('-d','--dry-run',
                      dest='dryrun',
                      action='store_true',
                      default=False,
                      help='show selections but do not run servos')
    parser.add_option('-r','--left','--marilyn',
                      action='store_true',
                      default=False,
                      help='Run left for Marilyn')
                      
    parser.add_option('-l','--right', '--donna',
                      action='store_true',
                      default=False,
                      help='Run right feeder for Donna')
    parser.add_option('-b','--both',
                      action='store_true',
                      default=False,
                      help='Feed both')
    
    cmdargs,remainder = parser.parse_args()

    feedLeft  = cmdargs.left
    feedRight = cmdargs.right
    if cmdargs.both:
        feedLeft  = True
        feedRight = True

    try:
        portionTime = float(remainder[0])
    except IndexError:
        portionTime = 1.0
        
    verbose = cmdargs.verbose

    if cmdargs.dryrun:
        verbose=True

    if verbose:
        print "Verbose   = %s"%str(verbose)
        print "FeedRight = %s"%str(feedRight)
        print "FeedLeft  = %s"%str(feedLeft)
        print "FeedBoth  = %s"%str(cmdargs.both)
        print "Dry run   = %s"%str(cmdargs.dryrun)
        print "Portion   = %s seconds"%str(portionTime)
        
    # dryrun option selected, exit without running servos
    if cmdargs.dryrun:
        sys.exit(1)
    
    GPIO.setmode(GPIO.BCM)

    servo1Pin = 18
    servo2Pin = 23

    pulseFreq = 50.0 # Hertz
    dutyCycle = 10.5 # percent

    servo1 = Servo(servo1Pin,pulseFreq,dutyCycle)


    servo2 = Servo(servo2Pin,pulseFreq,dutyCycle)

    if feedLeft:
        servo1.run(portionTime)
    if feedRight:
        servo2.run(portionTime)
    
    GPIO.cleanup()
