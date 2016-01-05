import time
import sys
from threading import Thread
from Queue import Queue
from subprocess import Popen, PIPE

inputQueue = Queue()

class InputReader(Thread):
    """Just keeps reading input"""
    def __init__(self, queue):
        super(InputReader, self).__init__()
        self.daemon = True
        self.queue = queue
        
    def run(self):
        while True:
            result = raw_input()
            self.queue.put(result)

reader = InputReader(inputQueue)
reader.start()


def rawInputWithTimeout(prompt="", timeout=5.0):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    
    #Throw out input that came before we asked for it
    #This is technically not thread-safe but should be good enough.
    while not inputQueue.empty():
        inputQueue.get()
    try:
        result = inputQueue.get(block=True, timeout=timeout)
        #print "You entered", result
    except Exception, e:
        result = None
        #print "\nToo slow: %s" % (e,)
    return result
        
def readAfterDelay():
    time.sleep(20.0)
    result = rawInputWithTimeout("What is your desire? ")
    if result is None:
        print ""
    print "First read: ", result
        
    print "Are you sure?"
    result = rawInputWithTimeout()
    if result is None:
        print ""
    print "Second read: ", result
    
def ioTest():
    for x in xrange(10):
        time.sleep(1.0)
        print x
    
        
if __name__ == "__main__":
    readAfterDelay()    
    #tailRead("log.txt")    
    #ioTest()