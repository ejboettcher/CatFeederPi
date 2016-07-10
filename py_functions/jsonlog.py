"""
These are simple tools for using json files for cat feeder logging
using json files
"""

import json

class JsonLog(object):
    """ 
    create a JSON object for logging
    """

    logData = None
    jsonLogFile = None
    
    def __init__(self,jsonLogFile):

        # this object will read from the json file if it exists, and laod
        # a list of logfile information
        #
        # if the json file does not exist, we will create a new one
        # 
        
        # try to open and read the log file
        try:
            with open(jsonLogFile,'r') as f:
                logData = json.load(f)
        except IOError:
            # file does not exist, so create a new logData list
            logData = list()

        self.logData = logData
        self.jsonLogFile = jsonLogFile

    def logEvent(self,d):
        """
        log an event by:
        1: adding to event queue
        2: writing new json file

        d is a dictionary of event information
        """
        self.logData.append(d)
        self.writeLog()
        # no return
        return None

    def writeLog(self):
        """
        write out the log file
        """
        with open(self.jsonLogFile,'w') as f:
            json.dump(self.logData,f,indent=4)

        return None
