import re
import os
import os.path

#Empty frames before manipulation - does not seem to help
FramesBeforeManipulationInput = 0 
#Number of frames to buffer before manipulation
ManipulationBufferFrames = 10
#Number of times to repeat buffer and manipulation
ManipulationRepeat = 4
#Put these in between "pen lifts"
ManipulationBuffer = [(246, 10), (246, 11)]
#This one for 7
Manipulate7 = [
   (77, 185),
   (78, 185),
]
#This one for 5
Manipulate5 = [
   (77, 182),
   (66, 166),
   (52, 165),
   (51, 152),
   (82, 156),
]

def parseFontData():
   """
Output format:
dict key is char - upper case only for letters
  element is a dictionary:
    width: #
    input:
      list
        x: #, y: #
   """
   font_data = {}
   
   with open("font_desc.txt") as f:
      font_file_lines = f.readlines()
   
   current_char = None
   current_width = 0
   current_input = []
   empty_line_flag = False
   
   for line in font_file_lines:
      new_char = re.search("^(.)\n", line);
      width = re.search("^([0-9]+)x14\n", line);
      coord = re.search("^([0-9]+),([0-9]+)\n", line);
      empty = re.search("^\n", line);
      
      if new_char:
         #print new_char.groups()[0]
         if (current_char != None):
            # store font info for previous char
            font_data[current_char] = {"width": current_width, "input": current_input}
   
         current_char = new_char.groups()[0][0]
         current_width = 0
         current_input = []
         empty_line_flag = False
         #print current_char
   
      elif width:
         #print "\t" + width.groups()[0]
         current_width = int(width.groups()[0])
   
      elif coord:
         #print "\t\t" + coord.groups()[0] + "\t" + coord.groups()[1]
         if (empty_line_flag):
            current_input.append({"x": 0, "y": 0, "touch": False})
            empty_line_flag = False
         current_input.append({"x": int(coord.groups()[0]), "y": int(coord.groups()[1]), "touch": True})
   
      elif empty:
         empty_line_flag = True;
   
      else:
         print "Unhandled line: " + line
   
   #Add entry for space
   font_data[' '] = {"width": 4, "input": []}
   return font_data

FontData = parseFontData()

def convertTextToCoords(textToDisplay):
   """
   Convert lines of text to a screen's worth of pen input.
   Output
   """
   #Max number of output lines per line of text
   MAX_LINES = 2
   #Amount to indent on text wrap
   INDENT = 0
   #Screen height and width
   MAX_HEIGHT = 196
   MAX_WIDTH = 180
   #All chars have same height
   CHAR_HEIGHT = 14
   #Height for each line
   LINE_HEIGHT = 16
   
   # These track the position to draw the next char
   # We will start in the upper left corner
   current_x = 0
   current_y = 0
   
   # The pen input to draw the text
   input_queue = []
   # This is how many lines we have written from the current input line
   line_count = 1;
   
   for c in textToDisplay.upper():
      #Handle newline
      if c == "\n":
         current_y += LINE_HEIGHT
         #If we are at the bottom of the screen we are done
         if current_y > MAX_HEIGHT-CHAR_HEIGHT:
            break
         current_x = 0
         line_count = 1
         continue
      
      if c not in FontData:
         continue
      width = FontData[c]["width"]
      input = FontData[c]["input"]
   
      #If the current line is cut off keep skipping chars until we hit a newline
      if line_count > MAX_LINES:
         continue
      
      # line wrap and indent if necessary
      if current_x + width >= MAX_WIDTH:
         current_x = INDENT
         line_count += 1  
         # This enforces the line length limit
         # If at the max do not increment y here, it will happen when we hit a newline
         if line_count > MAX_LINES:
            continue
         current_y += LINE_HEIGHT
         #If we are at the bottom of the screen we are done
         if current_y > MAX_HEIGHT-CHAR_HEIGHT:
            break
         
      # Add the input for the character
      for coord in input:
         input_queue.append({"x": current_x + coord["x"], "y": current_y + coord["y"], "touch": coord["touch"]})

      # Add a pen lift in between characters
      input_queue.append({"x": 0, "y": 0, "touch": False})

      # Advance the X position by the width of the character, plus 1 to leave room between
      current_x += width + 1
      
   return input_queue

def writeDsm(textToDisplay, dsmFileName, answer=7):
   """
   Write lines of dsm input that will draw the text.
   |0|.............216 086 1|
   -The 1 means touch and the coords say where
   |0|.............234 192 0|
   -No touch, empty input
   """
   coords = convertTextToCoords(textToDisplay)
   if os.path.isfile(dsmFileName):
      os.remove(dsmFileName)
   dsmFile = open(dsmFileName, "w")
   dsmLine = "|0|.............%03d %03d %d|\n"
   
   #dsm lines for the buffer input
   bufferDsm = "".join([dsmLine % (c + (1,)) for c in ManipulationBuffer])
   
   #Initial buffer makes it work
   dsmFile.write(bufferDsm)
   
   for coord in coords:
      if coord["touch"]:
         dsm_x = 247 - coord["y"]
         dsm_y = 6 + coord["x"]
         dsmFile.write(dsmLine % (dsm_x, dsm_y, 1))
      else:
         dsmFile.write(bufferDsm)
         
   #Some empty frames - the lua loop runs one more time than the python xrange loop
   for i in xrange(FramesBeforeManipulationInput+1):
      dsmFile.write(dsmLine % (234, 192, 0))
      
   #Manipulation
   numberManipulation = Manipulate5 if answer == 5 else Manipulate7
   for i in xrange(ManipulationRepeat):
      for j in xrange(ManipulationBufferFrames):
         dsmFile.write(bufferDsm)
      for c in numberManipulation:
         dsmFile.write(dsmLine % (c + (1,)))
   
   #Some more empty frames
   for i in xrange(20):
      dsmFile.write("|0|.............%03d %03d %d|\n" % (234, 192, 0))
      
   dsmFile.close()
   
def writeLuaTest(textToDisplay, luaFileName, logFileName="log.txt", answer=7):
   coords = convertTextToCoords(textToDisplay)
   if os.path.isfile(luaFileName):
      os.remove(luaFileName)
   luaFile = open(luaFileName, "w")
   luaFile.write("""
--Test lua file generated by brain age scripts
--Source text is:

""".lstrip("\n"))
   luaFile.write("--" + "\n--".join(textToDisplay.split("\n")))
   luaFile.write("""
   
--Stylus input for no touch
local noTouch = { };
noTouch.x = 234;
noTouch.y = 192;
noTouch.touch = false;

--For touching
local touchInput = { };
touchInput.touch = true;

savestate.load(4);
""")
   
   luaInputFrame = """
touchInput.x = %d;
touchInput.y = %d;
touchInput.touch = %s;
stylus.set(touchInput);
emu.frameadvance();
"""
   
   #Assemble the lua for buffer frames
   bufferLua = ""
   for coord in ManipulationBuffer:
      bufferLua += luaInputFrame % (coord + ("true",))
      
   #This first buffer avoids early parse
   luaFile.write(bufferLua)
      
   #The actual input
   for coord in coords:
      if not coord["touch"]:
         luaFile.write(bufferLua)
         continue
      dsm_x = 247 - coord["y"]
      dsm_y = 6 + coord["x"]
      touch = "true" if coord["touch"] else "false"
      luaFile.write(luaInputFrame % (dsm_x, dsm_y, touch))
      
   #The manipulation input
   endManip = ""
   numberManipulation = Manipulate5 if answer == 5 else Manipulate7
   for coord in numberManipulation:
      endManip += luaInputFrame % (coord + ("true",))
      
   #This is the magic trick to get it to work.
   #We have some buffer before the real manipulation
   #And then repeat that multiple times
   endManip = "\n".join([bufferLua] * ManipulationBufferFrames) + endManip
   endManip = "\n".join([endManip] * ManipulationRepeat)
   
   #padding frames and manipulation
   luaFile.write("""
print("Done with drawing");
   
for i=0,%d do
   stylus.set(noTouch);
   emu.frameadvance();
end;
""" % (FramesBeforeManipulationInput,) + endManip + """
oldTotal = memory.readbyte(0x020E98E0);
oldCorrect = memory.readbyte(0x020E98E4);

for i=0,%d do
   stylus.set(noTouch);
   emu.frameadvance();
   
   newTotal = memory.readbyte(0x020E98E0);
   if newTotal ~= oldTotal then break end;
end;

newCorrect = memory.readbyte(0x020E98E4);

logfile = io.open("%s", "a");
if newCorrect == oldCorrect + 1 then
   print("Got the question correct!");
   logfile:write("PASS\\n");
   
elseif newTotal == oldTotal + 1 then
   print("Incorrect!");
   logfile:write("FAIL\\n");
else
   print("Did not advance");
   logfile:write("FAIL\\n");
end;
io.close(logfile);

emu.pause();
""" % (420, logFileName))
   luaFile.close()
   
tiggerText = """Do Tiggers like honey?
Tiggers don't like honey!
that sticky stuff is only fit
for heffalumps and woozles
You mean elephants and weasels?
That's what I said, heffalumps and woozles"""
microText = """micro500: any new images?
samurai_goroh_: oh
samurai_goroh_: Mmm, I just did one about Kid from Bastion
samurai_goroh_: I won't be making many more, I'll be on vacations after Christmas
micro500: ahh crap
micro500: we still need like 36 more
micro500: and so far most of them have been done by you :P"""

def testConverter():
   """loop through a string, find the char, look it up, add the input"""
   for coord in convertTextToCoords(microText):
      if (coord["touch"]):
         print str(coord["x"]) + "," + str(coord["y"])
      else:
         print ""
   
def testDsmWrite():
   writeDsm("twitch plays brain age!\nWill the answer be correct?", "test.dsm")
   
def testLuaWrite():
   writeLuaTest(microText, "test.lua", answer=7)
   #writeLuaTest(tiggerText, "test.lua", answer=7)
   #writeLuaTest("abcd", "test.lua", answer=7)


if __name__ == "__main__":
   #testConverter()   
   testDsmWrite()
   testLuaWrite()