#!/usr/bin/env python

import sched
import time
import datetime
import sys
import optparse
import jsonlog

try:
    import RPi.GPIO as GPIO
except ImportError:
    print "GPIO module for Raspberry Pi not installed!"

def time2sam(time):
    return time.hour*3600 + time.minute*60 + time.second


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

def feed(servoList,portionTimeList,period):
    """
    feed on a periodic basis,
    returns the feedtime
    """
    feedtime = datetime.datetime.now()
    print 'Feeding at: %s'%str(feedtime)

    totPortion = 0.0
    # run each servo the allocated amount of time
    for _servo,_portion in zip(servoList,portionTimeList):
        _servo.run(_portion)
        totPortion += _portion
        # log the event
        evtInfo = {'time':str(datetime.datetime.now()),
                   'event':_servo.name}
        feedLog.logEvent(evtInfo)
    
        
    # before exiting, schedule next feeding
    print "Scheduling next feeding in %d seconds"%(period-totPortion)
    scheduler.enter(period-totPortion,1,feed,(servoList,portionTimeList,period))

    return feedtime
    
def feedDaily(servoList,portionTimeList):
    """
    this is the function to feed the cats once a day
    servoList is a list of servos for this feeding
    portionTimeList is a list of times for each feeding
    """

    # schedule this feeding again in 24 hours = 86400 seconds
    return feed(servoList,portionTimeList,86400)
        
if __name__=='__main__':

    # this is a json file to hold feeding log information
    jsonLogFile = '/home/pi/log.json'
    feedLog = jsonlog.JsonLog(jsonLogFile)

    # each event in the log file should consist of:
    # time and event in a dictionary such as
    # event = {'time':str(datetime.datetime.now()),
    #          'event':'Donna'}
    
    # set up the servo control
    GPIO.setmode(GPIO.BCM)

    servo1Pin = 18
    servo2Pin = 23

    pulseFreq = 50.0 # Hertz
    dutyCycle = 10.5 # percent

    servo1 = Servo(servo1Pin,pulseFreq,dutyCycle)
    servo2 = Servo(servo2Pin,pulseFreq,dutyCycle)
    servo1.name = 'Marilyn'
    servo2.name = 'Donna'

    portionTime1 = 0.5  # marilyn, left
    portionTime2 = 1.0  # donna, right
    
    # set up the feeding schedule
    # feeding schedule
    feedAt = list()
    feedAt.append(datetime.time(5,0,0))  # Hour, minute, second
    feedAt.append(datetime.time(17,0,0))

    #feedAt.append(datetime.time(16,39,00))
    
    # generate a scheduler to run the feedings
    scheduler = sched.scheduler(time.time,time.sleep)

    # get the current time
    print "Current time is %s"%str(datetime.datetime.now())
    currTimeSam = time2sam(datetime.datetime.now())
    
    # for each feed at time, schedule the first job to run
    for _feedTime in feedAt:
        print 'Scheduling feeding at %s'%str(_feedTime)
        feedSam = time2sam(_feedTime) # get seconds after midnight
        deltaSam = feedSam - currTimeSam

        # increment to next day if wrap around
        if deltaSam <=0: deltaSam += 86400

        # scedule each event
        scheduler.enter(deltaSam,1,feedDaily,
                        ((servo1,servo2),(portionTime1,portionTime2)))

        #scheduler.enter(deltaSam,1,feed,
        #                ((servo1,servo2),(portionTime,portionTime),10))

    scheduler.run()
    GPIO.cleanup()
