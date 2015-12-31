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

from convert_text import writeDsm
from async_input import rawInputWithTimeout

SubmissionDsmFile = "submission.dsm"
SubmissionLogFile = "submissionLog.txt"

class SubmissionManager(Thread):
    """
    """
    def __init__(self, submissionQueue):
        super(SubmissionManager, self).__init__()
        
        self.submissionQueue = submissionQueue        
        self.reviewTime = 30.0   #Allowable review time in seconds
        
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
        writeDsm(self.displayText, "submission.dsm")
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
                return False
            if 'PASS' in result:
                self.publishSubmission()
                return False
            #Timeout check
            if time.time() - submissionTime > self.reviewTime:
                return False
            time.sleep(1.0)
        
    def humanReview(self):
        """Human review of the text. Uses a raw_input in a separate thread that runs asynchronously.
        """
        print "\nPlease review:\n"
        print self.displayText
        print "\n"
        result = rawInputWithTimeout("Acceptable? (y/n) >>> ", self.reviewTime)
        if result == 'exit':
            return 'exit'
        if result is None:
            print "<Timeout>"
            return False
        return 'y' in result.lower()
                
    def launchDesmumeTest(self):
        """Need a test that runs the input and makes sure it works.
           On getting the result the lua writes to the log file and the tail check reads the result.
        """
        def fakeDesmumeTest():
            time.sleep(1)
            with open(SubmissionLogFile, "a") as submissionLog:
                submissionLog.write("PASS\n")
                
        #Eventual plan is that this gets run by simply overwriting a lua file.
        #Desmume would stay open and not be managed by this script other than through that lua.
        #For our fake version here we will not worry about it after starting it
        self.desmumeThread = Thread(target=fakeDesmumeTest)
        self.desmumeThread.start()
        
    def publishSubmission(self):
        now = datetime.datetime.now()
        print "Publishing at %s:%s" % (now.hour, now.minute)
        publishFileName = "%s-%s-%s.dsm" % (now.hour, now.minute, now.second)
        os.rename(SubmissionDsmFile, publishFileName)
                
        
def testSubmissionManager():
    """The test keeps generating lines and sending them in batches to the manager.
    """
    submissionQueue = Queue()
    submissionManager = SubmissionManager(submissionQueue)
    submissionManager.start()
    
    lineList = []
    maxLines = 5
    while True:
        try:
            verseJson = json.loads(urllib2.urlopen("http://labs.bible.org/api/?passage=random&type=json").readline())
            verseText = verseJson[0]['text'].encode('ascii', 'ignore')
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