#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# pins 18 and 23 were used in
# https://github.com/videoman/RPICatFeeder/blob/master/Cat-Feeder-Button-pwm.py
servo1Pin = 18
servo2Pin = 23

# set up GPIO
GPIO.setup(servo1Pin,GPIO.OUT)
GPIO.setup(servo2Pin,GPIO.OUT)

# set up each servo
servo1 = GPIO.PWM(servo1Pin,50) # 50 is pulse frequency in Hz
servo2 = GPIO.PWM(servo2Pin,50)

servo1.start(10.5)              # 10.5 is duty cycle of pulse on
servo2.start(10.5)

time.sleep(10.)

servo1.stop()
servo2.stop()

# when done, do this to clear GPIO settings.
GPIO.cleanup()

