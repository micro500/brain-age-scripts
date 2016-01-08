import os
import os.path
import sys

from ds_stream import TasbotStreamerBase, FakeSerialInterface

ImagesDir = "../tas_projects/AGDQ2016/finished_images/"
PublishDir = "./twitch_plays/publish/"

EmptyDsmLine = "|0|.............000 000 0|\n"
      
class DsStreamer(TasbotStreamerBase):
   """Like the normal streamer it goes through a series of files.
      However the list of files comes from the file_list.txt file or other specified file.
      If it lists "<twitch>" as one of its entries then it switches to twitch mode.
      Empty input is returned until a new file is found in the twitch_plays/publish dir.
      That dsm will be played and then it will switch back to the file list.
   """
   def __init__(self, serialInterface, fileListFile=None):
      super(DsStreamer, self).__init__(serialInterface)
      
      if fileListFile is None:
         fileListFile = os.path.join(ImagesDir, "file_list.txt")
      
      with open(fileListFile) as f:
         self.dsmFileList = [fname.strip() for fname in f.readlines()]
         
      self.inputFh = None
      self.waitingForTwitchImage = False
      self.lastTwitchImageSet = set()
         
   def getNextLine(self):
      if self.waitingForTwitchImage:
         self.checkTwitchImageDir()
         return EmptyDsmLine
      
      while (True):
         if self.inputFh is None:
            #At the end of the file list? Then we are done!
            if len(self.dsmFileList) == 0:
               sys.exit(0)
            nextFileName = self.dsmFileList.pop(0)
            
            #Begin twitch sequence
            if nextFileName == "<twitch>":
               self.handleTwitchBegin()
               return EmptyDsmLine
            
            #Open the next file or skip on failure
            actualFileName = os.path.join(ImagesDir, nextFileName)
            if not os.path.isfile(actualFileName):
               print "File not found: " + fileName
               continue
            
            self.inputFh = open(actualFileName)
            
         fbuf = self.inputFh.readline()
   
         if not fbuf:
            self.inputFh.close()
            self.inputFh = None
         elif fbuf[0] != "|":
            pass
         else:
            return fbuf      
         
   def handleTwitchBegin(self):
      """On beginning twitch phase, check the publish dir"""
      self.waitingForTwitchImage = True
      self.lastTwitchImageSet = set(os.listdir(PublishDir))
      
   def checkTwitchImageDir(self):
      """Check the twitch image dir. If a new image was published then start streaming from it"""
      newImages = set(os.listdir(PublishDir)) - self.lastTwitchImageSet
      if len(newImages) == 0:
         return
      
      #Clear the waiting flag and open the file
      self.waitingForTwitchImage = False
      self.inputFh = open(os.path.join(PublishDir, newImages.pop()))
   
   def getFilesInPublishDir(self):
      return set(os.listdir(PublishDir))

   
def main():
   if len(sys.argv) < 2:
      sys.stderr.write('Usage: ' + sys.argv[0] + ' <interface> (<list_file>)\n\n')
      return
   
   serialName = sys.argv[1]
   if serialName == "fake":
      ser = FakeSerialInterface()
   else:
      import serial
      baud = 9600
      ser = serial.Serial(sys.argv[1], baud, timeout = 0)
      
   if len(sys.argv) > 2:
      list_file = sys.argv[2]
   else:
      list_file = os.path.join(ImagesDir, "file_list.txt")
   
   streamer = DsStreamer(ser)
   streamer.runStream()

   
if __name__ == "__main__":
   main()