import os
import sys

class TasbotStreamerBase(object):
   def __init__(self, serialInterface):
      self.ser = serialInterface
      
      self.framecount = 0
      
   def runStream(self):
      """Play the stream"""
      # send the first 20 frames
      for i in range(1, 20):
         self.sendNextFrame()
      
      print ""
      
      while(True):
         #Wait until board has something to say
         while (self.ser.inWaiting() == 0):
            pass
      
         #The board sends an f when it is ready for the next frame
         c = self.ser.read()
         if (c == 'f'):
            self.framecount += 1
            self.sendNextFrame()
   
   def sendNextFrame(self):
      """reads the next input and returns appropriately formatted data"""
      fbuf = self.getNextLine()
   
      if (int(fbuf[24:25]) == 1):
         print "c Y %0.3X" % (int(fbuf[16:19]) * 16) + " " + "%0.3X" % (int(fbuf[20:23]) * 16 + 512) + " f";
         self.ser.write("c Y %0.3X" % (int(fbuf[16:19]) * 16) + " " + "%0.3X" % (int(fbuf[20:23]) * 16 + 512) + " f")
      else:
         print "c N f";
         self.ser.write("c N f")

   def getNextLine(self):
      """Virtual"""
      raise NotImplementedError("getNextLine is virtual in base class")
   
   
class TasbotFileStreamer(TasbotStreamerBase):
   def __init__(self, serialInterface, inputFileOrList):
      super(TasbotFileStreamer, self).__init__(serialInterface)
      
      self.inputFileList = inputFileOrList if hasattr(inputFileOrList, "__iter__") else [inputFileOrList]
      self.nextFileIndex = 0
      self.inputFh = None
      
   def getNextLine(self):
      while (True):
         if self.inputFh is None:
            if self.nextFileIndex > len(self.inputFileList) - 1:
               sys.exit(0)
            self.inputFh = open(self.inputFileList[self.nextFileIndex], 'r')
            self.nextFileIndex += 1
            
         fbuf = self.inputFh.readline()
   
         if (not fbuf):
            self.inputFh.close()
            self.inputFh = None
         elif (fbuf[0:1] == "#"):
            pass
         else:
            return fbuf
         

class FakeSerialInterface(object):
   def __init__(self):
      pass
   
   def inWaiting(self):
      return 1
   
   def read(self):
      return 'f'
   
   def write(self, buf):
      pass
      #print "wrote to fake serial output: " + buf
   
         
def main():
   """Load serial interface and files from command line args"""
   if len(sys.argv) < 3:
      sys.stderr.write('Usage: ' + sys.argv[0] + ' <interface> <replayfile> [replayfile] ...\n\n')
      sys.exit(0)
   
   serialName = sys.argv[1]
   if serialName == "fake":
      ser = FakeSerialInterface()
   else:
      import serial
      baud = 9600
      ser = serial.Serial(sys.argv[1], baud, timeout = 0)
   
   fileList = []
   for i in xrange(2, len(sys.argv)):
      fileList.append(sys.argv[i])
   
   streamer = TasbotFileStreamer(ser, fileList)
   streamer.runStream()

   
if __name__ == "__main__":
   main()