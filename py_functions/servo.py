#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import sys

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

    GPIO.setmode(GPIO.BCM)

    servo1Pin = 18
    servo2Pin = 23

    pulseFreq = 50.0 # Hertz
    dutyCycle = 10.5 # percent

    portionTime = float(sys.argv[1])

    servo1 = Servo(servo1Pin,pulseFreq,dutyCycle)
    servo1.run(portionTime)

    servo2 = Servo(servo2Pin,pulseFreq,dutyCycle)
    servo2.run(portionTime)
    
    GPIO.cleanup()
