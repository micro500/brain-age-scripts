import sys
import time
import os
import os.path
import re

from keyboard import createKeyboardInput

FirmwareDsmFileName = "brain_age_firmware.dsm"
MainDsmFileName = "brain_age.dsm"

def main():
   if len(sys.argv) < 2:
      sys.stderr.write('Usage: ' + sys.argv[0] + ' <string> \n\n')
      sys.exit(0)
   
   firmwareText = sys.argv[1]
   
   if os.path.isfile(FirmwareDsmFileName):
      os.remove(FirmwareDsmFileName)
   firmwareDsm = open(FirmwareDsmFileName, "w")
   
   beforeDsm = open("../tas_projects/AGDQ2016/finished_images/other/firmware_before_name.dsm")
   for line in beforeDsm:
      if re.match("\s*#", line):
         continue
      #Ensure that every line including last has a newline
      firmwareDsm.write(line.rstrip("\n") + "\n")
   beforeDsm.close()
   
   firmwareDsm.write(createKeyboardInput(firmwareText))
   
   afterDsm = open("../tas_projects/AGDQ2016/finished_images/other/firmware_after_name.dsm")
   for line in afterDsm:
      if re.match("\s*#", line):
         continue
      #Ensure that every line including last has a newline
      firmwareDsm.write(line.rstrip("\n") + "\n")
   afterDsm.close()
   
   firmwareDsm.close()
   
   with open("../tas_projects/AGDQ2016/finished_images/file_list.txt") as f:
      dsmFileList = [fname.rstrip("\n") for fname in f.readlines()]
   
   if os.path.isfile(MainDsmFileName):
      os.remove(MainDsmFileName)
   mainDsm = open(MainDsmFileName, "w")
   
   for fileName in dsmFileList:
      #Filename is relative to that finished_images dir. Get path from this dir.
      actualFileName = os.path.join("../tas_projects/AGDQ2016/finished_images/", fileName)
      if not os.path.isfile(actualFileName):
         print "File not found: " + fileName
         continue
      dsmFile = open(actualFileName)
      for line in dsmFile:
         mainDsm.write(line)
      dsmFile.close()
   
   mainDsm.close()
      

if __name__ == "__main__":
   main()