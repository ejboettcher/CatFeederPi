#!/usr/bin/env python
"""
Usage: servo.py [--verbose] [--dry-run] 
                (--right|--left|--both|--donna|--marilyn)
                [PORTION-TIME]
       servo.py [PORTION-TIME]
                
       servo.py --help  

Arguments:
 PORTION-TIME          time allocated for each portion [default: 1.0]

Options:
 -h --help             show this help message and exit
 -v --verbose          turn on verbose mode
 -d --dry-run          dry-run, print out actions, but don't act
 -r --right --marilyn  feed marilyn on right
 -l --left --donna     feed donna on left
 -b --both             feed both
"""

import time
import sys
import optparse
from docopt import docopt
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


    docopt_args = docopt(__doc__)

    feedLeft    = docopt_args['--left']
    feedRight   = docopt_args['--right']

    feedDonna   = docopt_args['--donna']
    feedMarilyn = docopt_args['--marilyn']

    if feedDonna: feedRight = True
    if feedMarilyn: feedLeft = True
    
    if docopt_args['--both']:
        feedLeft  = True
        feedRight = True
        
    verbose = docopt_args['--verbose']

    dryrun = docopt_args['--dry-run']
    if dryrun:
        verbose=True

    portionTime = docopt_args['PORTION-TIME']
    if portionTime is None: portionTime = 1.0
    portionTime = float(portionTime)
    
    if verbose:
        print "Verbose   = %s"%str(verbose)
        print "FeedRight = %s"%str(feedRight)
        print "FeedLeft  = %s"%str(feedLeft)
        print "FeedBoth  = %s"%str(docopt_args['--both'])
        print "Dry run   = %s"%str(dryrun)
        print "Portion   = %s seconds"%str(portionTime)
        
    # dryrun option selected, exit without running servos
    if dryrun:
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
