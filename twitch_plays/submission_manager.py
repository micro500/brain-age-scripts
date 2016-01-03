import sys
import logging
import re
import os
import time
from threading import Thread
import traceback
from Queue import Queue
import datetime
import urllib2, json

from convert_text import writeDsm, writeLuaTest
from async_input import rawInputWithTimeout

TargetAnswer = 5

SubmissionDsmFile = "submission.dsm"
SubmissionLuaFile = "submission.lua"
SubmissionLogFile = "submissionLog.txt"

DesmumeCheckLogFile = "desmumeCheckLog.txt"

class SubmissionManager(Thread):
    """
    """
    def __init__(self, submissionQueue):
        super(SubmissionManager, self).__init__()
        
        self.submissionQueue = submissionQueue        
        self.totalReviewTime = 300.0   #Allowable review time in seconds
        self.humanReviewTime = self.totalReviewTime   #Allowable review time in seconds
        self.defaultHumanResponse = False  #Human review result on timeout - should be False but True is useful for testing
        
    def run(self):
        done = False
        while not done:
            done = self.processSubmission()
        print "Exiting submission manager"
        
    def processSubmission(self):
        self.displayText = self.submissionQueue.get()  #This waits until something gets put into queue
        #print "New submission!"
        
        if self.displayText is None:
            return True
        
        if os.path.isfile(SubmissionLogFile):
            os.remove(SubmissionLogFile)
        if os.path.isfile(SubmissionDsmFile):
            os.remove(SubmissionDsmFile)
        
        #Create a new log file so we can tail it
        with open(SubmissionLogFile, "a"):
            os.utime(SubmissionLogFile, None)
        
        submissionTime = time.time()
        writeDsm(self.displayText, "submission.dsm", answer=TargetAnswer)
        self.launchDesmumeTest()
        
        #Human review - if rejected then move on to next submission
        humanReviewResult = self.humanReview()
        if humanReviewResult == 'exit':
            return True
        elif not humanReviewResult:
            return False
        
        #Check the log file every second to see if desmume finished
        while True:
            with open(SubmissionLogFile) as submissionLog:
                result = submissionLog.readline()
            if 'FAIL' in result:
                self.logDesmumeCheckResult("FAIL")
                return False
            if 'PASS' in result:
                self.logDesmumeCheckResult("PASS")
                self.publishSubmission()
                return False
            #Timeout check
            if time.time() - submissionTime > self.totalReviewTime:
                self.logDesmumeCheckResult("TIMEOUT")
                return False
            time.sleep(1.0)
            
    def logDesmumeCheckResult(self, result):
        with open(DesmumeCheckLogFile, "a"):
            os.utime(DesmumeCheckLogFile, None)
        now = datetime.datetime.now()
        with open(DesmumeCheckLogFile, "a") as desmumeLogFile:
            desmumeLogFile.write("%s:%s - %s\n\n" % (now.hour, now.minute, result))
            desmumeLogFile.write(self.displayText)
            desmumeLogFile.write("\n")
        
    def humanReview(self):
        """Human review of the text. Uses a raw_input in a separate thread that runs asynchronously.
        """
        print "\nPlease review:\n"
        print self.displayText
        print "\n"
        result = rawInputWithTimeout("Acceptable? (y/n) >>> ", self.humanReviewTime)
        if result == 'exit':
            return 'exit'
        if result is None:
            print "<Timeout>"
            return self.defaultHumanResponse
        return 'y' in result.lower()
                
    def launchDesmumeTest(self):
        """Need a test that runs the input and makes sure it works.
           On getting the result the lua writes to the log file and the tail check reads the result.
           Note that this script does not take care of setting up Desmume!
           To make this work desmume needs to be opened with savestate number 4 set at the point where
           the text will be drawn. The lua file needs to be loaded. Then each time this script rewrites
           it, it will run again.
        """
        writeLuaTest(self.displayText, SubmissionLuaFile, logFileName=SubmissionLogFile, answer=TargetAnswer)
        
    def publishSubmission(self):
        now = datetime.datetime.now()
        print "Publishing at %s:%s" % (now.hour, now.minute)
        publishFileName = "./publish/%s-%s-%s-answer%s.dsm" % (now.hour, now.minute, now.second, TargetAnswer)
        os.rename(SubmissionDsmFile, publishFileName)
                
        
def testSubmissionManager():
    """The test keeps generating lines and sending them in batches to the manager.
    """
    submissionQueue = Queue()
    submissionManager = SubmissionManager(submissionQueue)
    submissionManager.humanReviewTime = 8.0
    self.defaultHumanResponse = True
    submissionManager.start()
    
    lineList = []
    maxLines = 6
    while True:
        try:
            verseJson = json.loads(urllib2.urlopen("http://labs.bible.org/api/?passage=random&type=json").readline())
            verseText = verseJson[0]['text'].encode('ascii', 'ignore').rstrip("\n")
            lineList.append(verseText)
            if len(lineList) > maxLines:
                lineList.pop(0)
            #print u"Got line %d: %s" % (len(lineList), verseText)
            #If we have a full list and empty queue then send it away
            #Then start over while submission process happens
            if len(lineList) == maxLines and submissionQueue.empty():
                submissionQueue.put("\n".join(lineList), block=False)
                lineList = []
                
            if not submissionManager.isAlive():
                break
            
        except Exception, e:
            print "Exception somewhere: " + str(e)
        
        time.sleep(4.0)


if __name__ == "__main__":
    testSubmissionManager()