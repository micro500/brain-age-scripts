import sys
import time

regular_keys_x = {
   '1': 51,
   '2': 67,
   '3': 83,
   '4': 99,
   '5': 115,
   '6': 131,
   '7': 147,
   '8': 163,
   '9': 179,
   '0': 195,
   '-': 211,
   '=': 227,
   'q': 60,
   'w': 76,
   'e': 92,
   'r': 108,
   't': 124,
   'y': 140,
   'u': 156,
   'i': 172,
   'o': 188,
   'p': 204,
   'backspace': 225,
   'caps': 50,
   'a': 67,
   's': 83,
   'd': 99,
   'f': 115,
   'g': 131,
   'h': 147,
   'j': 163,
   'k': 179,
   'l': 196,
   'shift': 54,
   'z': 75,
   'x': 91,
   'c': 107,
   'v': 123,
   'b': 139,
   'n': 155,
   'm': 171,
   ',': 187,
   '.': 203,
   '/': 219,
   ';': 83,
   '\'': 99,
   ' ': 147,
   '[': 195,
   ']': 211};

regular_keys_y = {
   '1': 72,
   '2': 72,
   '3': 72,
   '4': 72,
   '5': 72,
   '6': 72,
   '7': 72,
   '8': 72,
   '9': 72,
   '0': 72,
   '-': 72,
   '=': 72,
   'q': 87,
   'w': 87,
   'e': 87,
   'r': 87,
   't': 87,
   'y': 87,
   'u': 87,
   'i': 87,
   'o': 87,
   'p': 87,
   'backspace': 87,
   'caps': 103,
   'a': 103,
   's': 103,
   'd': 103,
   'f': 103,
   'g': 103,
   'h': 103,
   'j': 103,
   'k': 103,
   'l': 103,
   'shift': 119,
   'z': 119,
   'x': 119,
   'c': 119,
   'v': 119,
   'b': 119,
   'n': 119,
   'm': 119,
   ',': 119,
   '.': 119,
   '/': 119,
   ';': 135,
   '\'': 135,
   ' ': 135,
   '[': 135,
   ']': 135};

shift_keys_x = {
   '!': 51,
   '@': 67,
   '#': 83,
   '$': 99,
   '%': 115,
   '^': 131,
   '&': 147,
   '*': 163,
   '(': 179,
   ')': 195,
   '_': 211,
   '+': 227,
   'Q': 60,
   'W': 76,
   'E': 92,
   'R': 108,
   'T': 124,
   'Y': 140,
   'U': 156,
   'I': 172,
   'O': 188,
   'P': 204,
   '': 225,
   '': 50,
   'A': 67,
   'S': 83,
   'D': 99,
   'F': 115,
   'G': 131,
   'H': 147,
   'J': 163,
   'K': 179,
   'L': 196,
   '': 54,
   'Z': 75,
   'X': 91,
   'C': 107,
   'V': 123,
   'B': 139,
   'N': 155,
   'M': 171,
   '<': 187,
   '>': 203,
   '?': 219,
   ':': 83,
   '~': 99,
   '': 147,
   '{': 195,
   '}': 211}

shift_keys_y = {
   '!': 72,
   '@': 72,
   '#': 72,
   '$': 72,
   '%': 72,
   '^': 72,
   '&': 72,
   '*': 72,
   '(': 72,
   ')': 72,
   '_': 72,
   '+': 72,
   'Q': 87,
   'W': 87,
   'E': 87,
   'R': 87,
   'T': 87,
   'Y': 87,
   'U': 87,
   'I': 87,
   'O': 87,
   'P': 87,
   '': 87,
   '': 103,
   'A': 103,
   'S': 103,
   'D': 103,
   'F': 103,
   'G': 103,
   'H': 103,
   'J': 103,
   'K': 103,
   'L': 103,
   '': 119,
   'Z': 119,
   'X': 119,
   'C': 119,
   'V': 119,
   'B': 119,
   'N': 119,
   'M': 119,
   '<': 119,
   '>': 119,
   '?': 119,
   ':': 135,
   '~': 135,
   '': 135,
   '{': 135,
   '}': 135
}


def createKeyboardInput(text):
   dsmLines = ""
   dsmLine = "|0|.............%03d %03d %d|\n"
   
   for i in xrange(11):
      dsmLines += dsmLine % (225, 87, 1)
      dsmLines += dsmLine % (0, 0, 0)

   for c in text:
      if c in regular_keys_x:
         dsmLines += dsmLine % (regular_keys_x[c], regular_keys_y[c], 1)
         dsmLines += dsmLine % (0, 0, 0)
      elif c in shift_keys_x:
         dsmLines += dsmLine % (54, 119, 1)
         dsmLines += dsmLine % (0, 0, 0)
         dsmLines += dsmLine % (shift_keys_x[c], shift_keys_y[c], 1)
         dsmLines += dsmLine % (0, 0, 0)
      else:
         print "Unhandled: " + c
         
   return dsmLines

def testKeyboardInput():
   """Print the dsm output for some text given on the command line"""
   if len(sys.argv) < 2:
      sys.stderr.write('Usage: ' + sys.argv[0] + ' <string> \n\n')
      sys.exit(0)
   
   text = sys.argv[1]
   print createKeyboardInput(text)

if __name__ == "__main__":
   testKeyboardInput()