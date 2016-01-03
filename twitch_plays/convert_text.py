import re
import os
import os.path

FramesBeforeManipulationInput = 0 

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
         current_y += LINE_HEIGHT
         #If we are at the bottom of the screen we are done
         if current_y > MAX_HEIGHT-CHAR_HEIGHT:
            break
         current_x = INDENT
         line_count += 1  
         # This enforces the line length limit
         if line_count > MAX_LINES:
            continue
         
      # Add the input for the character
      for coord in input:
         input_queue.append({"x": current_x + coord["x"], "y": current_y + coord["y"], "touch": coord["touch"]})

      # Add a pen lift in between characters
      input_queue.append({"x": 0, "y": 0, "touch": False})

      # Advance the X position by the width of the character, plus 1 to leave room between
      current_x += width + 1
      
   return input_queue

def testConverter():
# loop through a string, find the char, look it up, add the input
   textToDisplay = """micro500: any new images?
samurai_goroh_: oh
samurai_goroh_: Mmm, I just did one about Kid from Bastion
samurai_goroh_: I won't be making many more, I'll be on vacations after Christmas
micro500: ahh crap
micro500: we still need like 36 more
micro500: and so far most of them have been done by you :P"""

   for coord in convertTextToCoords(textToDisplay):
      if (coord["touch"]):
         print str(coord["x"]) + "," + str(coord["y"])
      else:
         print ""
      
def writeDsm(textToDisplay, dsmFileName):
   """
   Write lines of dsm input that will draw the text.
   |0|.............216 086 1|
   -The 1 means touch and the coords say where
   |0|.............000 000 0|
   -No touch, empty input
   """
   coords = convertTextToCoords(textToDisplay)
   if os.path.isfile(dsmFileName):
      os.remove(dsmFileName)
   dsmFile = open(dsmFileName, "w")
   for coord in coords:
      dsm_x = 247 - coord["y"]
      dsm_y = 6 + coord["x"]
      touch = 1 if coord["touch"] else 0
      dsmFile.write("|0|.............%03d %03d %d|\n" % (dsm_x, dsm_y, touch))
      
   #Some empty frames
   for i in xrange(FramesBeforeManipulationInput):
      dsmFile.write("|0|.............%03d %03d %d|\n" % (0, 0, 0))
      
   #Manipulate a 7
   dsmFile.write("|0|.............%03d %03d %d|\n" % (77, 185, 1))
   dsmFile.write("|0|.............%03d %03d %d|\n" % (78, 185, 1))
   
   #Some more empty frames
   for i in xrange(20):
      dsmFile.write("|0|.............%03d %03d %d|\n" % (0, 0, 0))
      
   dsmFile.close()
   
def writeLuaTest(textToDisplay, luaFileName):
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
   
   #Try to avoid early parse
   manipLua = ""
   for coord in [(246, 10), (246, 11)]:
      manipLua += """
touchInput.x = %d;
touchInput.y = %d;
touchInput.touch = true;
stylus.set(touchInput);
emu.frameadvance();
""" % coord
   luaFile.write(manipLua)
      
   #The actual input
   for coord in coords:
      if not coord["touch"]:
         luaFile.write(manipLua)
         continue
      dsm_x = 247 - coord["y"]
      dsm_y = 6 + coord["x"]
      touch = "true" if coord["touch"] else "false"
      luaFile.write("""
touchInput.x = %d;
touchInput.y = %d;
touchInput.touch = %s;
stylus.set(touchInput);
emu.frameadvance();
""" % (dsm_x, dsm_y, touch))
      
   #The manipulation input
   #TODO: both of these were provided by xy2_ or micro500 but they do not seem to work!
   #This one for 7
   manipCoords = [
      (77, 185),
      (78, 185),
   ]
   #This one for 5
   manipCoords = [
      (77, 182),
      (66, 166),
      (52, 165),
      (51, 152),
      (82, 156),
   ]
   endManip = ""
   for coord in manipCoords:
      endManip += """
touchInput.x = %d;
touchInput.y = %d;
touchInput.touch = true;
stylus.set(touchInput);
emu.frameadvance();
""" % coord
   #Something else I tried
   endManip = "\n".join([manipLua] * 5) + endManip
   
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
end;

newTotal = memory.readbyte(0x020E98E0);
newCorrect = memory.readbyte(0x020E98E4);

logfile = io.open("log.txt", "a");
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
""" % (120,))
   luaFile.close()
   
def testDsmWrite():
   textToDisplay = """micro500: any new images?
samurai_goroh_: oh
samurai_goroh_: Mmm, I just did one about Kid from Bastion
samurai_goroh_: I won't be making many more, I'll be on vacations after Christmas
micro500: ahh crap
micro500: we still need like 36 more
micro500: and so far most of them have been done by you :P"""
   writeDsm(textToDisplay, "test.dsm")
   
def testLuaWrite():
   textToDisplay = """Do Tiggers like honey?
Tiggers don't like honey!
that sticky stuff is only fit
for heffalumps and woozles
You mean elephants and weasels?
That's what I said, heffalumps and woo
""".rstrip("\n")
#That's what I said, heffalumps and woozles
   writeLuaTest(textToDisplay, "test.lua")
   #writeLuaTest("abcd", "test.lua")


if __name__ == "__main__":
   #testConverter()   
   #testDsmWrite()
   testLuaWrite()