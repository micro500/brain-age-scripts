import re

# list key 0-255 (ascii code)
#   element is a dictionary:
#     width: #
#     input:
#       list
#         x: #, y: #

font_data = []

for i in range(0,256):
  font_data.append({"width": 0, "input": []})

with open("font_desc.txt") as f:
    font_file_lines = f.readlines()
    
current_char = -1
current_width = 0
current_input = []
empty_line_flag = False
    
for line in font_file_lines:
  new_char = re.search("^(.)\n", line);
  width = re.search("^([0-9]+)x14\n", line);
  coord = re.search("^([0-9]+),([0-9]+)\n", line);
  empty = re.search("^\n", line);
  if new_char:
#    print new_char.groups()[0]
    if (current_char != -1):
      # store font info for previous char
      font_data[current_char] = {"width": current_width, "input": current_input}
      
      # Also copy this data to other similar characters
      # TODO
#      print current_input
      
    current_char = ord(new_char.groups()[0][0])
    current_width = 0
    current_input = []
    empty_line_flag = False
#    print current_char
      
  elif width:
#    print "\t" + width.groups()[0]
    current_width = int(width.groups()[0])
    
  elif coord:
#    print "\t\t" + coord.groups()[0] + "\t" + coord.groups()[1]
    if (empty_line_flag):
      current_input.append({"x": 0, "y": 0, "touch": False})
      empty_line_flag = False
    current_input.append({"x": int(coord.groups()[0]), "y": int(coord.groups()[1]), "touch": True})
    
  elif empty:
#    print ""
    empty_line_flag = True;
    
  else:
    print "Unhandled line: " + line
    
font_data[32] = {"width": 4, "input": []}

#for i in range(0,256):
#  print str(i) + ": " ;
#  print font_data[i]

# loop through a string, find the char, look it up, add the input
string_to_display = "micro500: any new images?\nsamurai_goroh_: oh\nsamurai_goroh_: Mmm, I just did one about Kid from Bastion\nsamurai_goroh_: I won't be making many more, I'll be on vacations after Christmas\nmicro500: ahh crap\nmicro500: we still need like 36 more\nmicro500: and so far most of them have been done by you :P"
string_to_display = string_to_display.upper()

# We will start in the upper left corner
current_x = 0
current_y = 0

input_queue = []

line_count = 0;

for c in string_to_display:
  index = ord(c)
  width = font_data[index]["width"]
  input = font_data[index]["input"]
  
  if (index == 10):
    current_y = current_y + 16
    current_x = 0
    line_count = 0
  else:
    if (current_x + width >= 180 and line_count == 0):
      # line wrap and indent
      current_y = current_y + 16
      current_x = 0
      line_count = 1  
    if (current_y <= 196-14 and current_x + width < 180):
      for coord in input:
        input_queue.append({"x": current_x + coord["x"], "y": current_y + coord["y"], "touch": coord["touch"]})
      
      # Add a pen lift in between characters
      input_queue.append({"x": 0, "y": 0, "touch": False})
        
    # Advance the X position by the width of the character, plus 1 to leave room between
    current_x = current_x + width + 1
  
for coord in input_queue:
  if (coord["touch"]):
    print str(coord["x"]) + "," + str(coord["y"])
  else:
    print ""
