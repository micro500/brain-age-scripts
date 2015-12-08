import os
import serial
import sys
import time

# if you have a game fix ID, enter it here
game_fix = 0
ubw_p1 = 0
ubw_p2 = 0

####

baud = 9600

####

ver_max = ['1', '1']

prebuffer = 30

####

framecount = 0
firstline = 0
totalframes = 0

latches = '1'
timeout = 0

bits_source = 0

p = {}
plog = []

filecount = 0;

####

if len(sys.argv) < 3:
        sys.stderr.write('Usage: ' + sys.argv[0] + ' <interface> <replayfile> [replayfile] ...\n\n')
        sys.exit(0)

#if not os.path.exists(sys.argv[1]):
#        sys.stderr.write('Error: "' + sys.argv[1] + '" not found\n')
#        sys.exit(1)


# open the file and get the extension
fh = open(sys.argv[2], 'r')

ser = serial.Serial(sys.argv[1], baud, timeout = 0)


# all done... print out info, wait X frames, then tell the device to stop
def cleanup():
        global prebuffer
        global framecount
        global p

        wait = prebuffer

        while (wait):
                while (ser.inWaiting() == 0):
                        pass

                ser.read()
                wait -= 1

                # update with fake information
                p = plog.pop(0)

                framecount[0] += 1
                printinfo()

        # ser.write("~V")
        #time.sleep(0.001)
        time.sleep(2.001)
        # ser.write("~r")

        if (ubw_p1):
                disp_p1.write('O,0,255,0' + chr(0x0d) + chr(0x0a))
        if (ubw_p2):
                disp_p2.write('O,0,255,0' + chr(0x0d) + chr(0x0a))

        print("\r\nDone.")
        sys.exit(0)


def printinfo():
        global prebuffer
        global start
        global framecount
        global totalframes
        global tskip

        if (framecount == [tskip + prebuffer + 1, 0]):
                sys.stdout.write("Resetting...")
                start = time.time()
        else:
                ct = time.time()
                frameadj = framecount[0] - prebuffer
                if (ftype == '.fm2'):
                        out = "%6u/%6u (%u lag + %u std), %5.2fms, %01u:%02u:%05.2fs " % (
                                frameadj + framecount[1], totalframes, framecount[1], frameadj,
                                (ct - t) * 1000,
                                (ct - start) / 3600, ((ct - start) / 60) % 60, (ct - start) % 60)
                else:
                        out = "%6u/%6u (+%u lag = %u), %5.2fms, %01u:%02u:%05.2fs " % (
                                frameadj, totalframes, framecount[1], frameadj + framecount[1],
                                (ct - t) * 1000,
                                (ct - start) / 3600, ((ct - start) / 60) % 60, (ct - start) % 60)

                sys.stdout.write(out)

                if (fm[0] == '8'):
                        sys.stdout.write("  " + display_nes())

                if (lagnow):
                        sys.stdout.write(" **LAG**")

        sys.stdout.write("\033[K\r")
        sys.stdout.flush()



# seek to beginning of file, read out amount of bytes to skip
def fh_setup(skip):
        global fh
        global fbuf

        fh.seek(0)

        if (ftype == '.fm2'):
                a = 0
                while (a < firstline + skip):
                        fbuf = fh.readline()
                        a += 1
        if (ftype[0:2] == '.r'):
                # .rXX does not support skipping
                pass


# gets X bits for p1 then X bits for p2 sequentially
def raw_getbits(bytes):
        b = {}

        if (ftype == '.r16m'):
                for x in range(0, 8):
                        b[x] = fh.read(bytes)
        elif (ftype == '.r08'):
                for x in range(0, 8):
                        b[x] = chr(0)
                b[0] = fh.read(bytes)	# p1d0
                b[4] = fh.read(bytes)	# p2d0

        if (len(b[0]) == 0):
                # end of file...
                cleanup()
                return false

        if (bytes == 1):
                for x in range(0, 8):
                        b[x] = ord(b[x][0]) << 24;
        if (bytes == 2):
                for x in range(0, 8):
                        b[x] = ord(b[x][0]) << 24 | ord(b[x][1]) << 16;
        if (bytes == 4):
                pass

        return b

# gets X bits for p1 then X bits for p2 sequentially
def raw_getbits_twitch(bytes):
        b = {}

        b[0] = bs.getNextBits() << 16
        b[4] = bs.getNextBits() << 16

        b[2] = 0
        b[3] = 0

        b[1] = bs.getNextBits() << 16
        b[5] = bs.getNextBits() << 16

        b[6] = 0
        b[7] = 0

        b[0] = ((b[0] & 0xFF000000) >> 8) | ((b[0] & 0x00FF0000) << 8)
        b[1] = ((b[1] & 0xFF000000) >> 8) | ((b[1] & 0x00FF0000) << 8)
        b[4] = ((b[4] & 0xFF000000) >> 8) | ((b[4] & 0x00FF0000) << 8)
        b[5] = ((b[5] & 0xFF000000) >> 8) | ((b[5] & 0x00FF0000) << 8)


        # if (len(b[0]) == 0):
                # # end of file...
                # cleanup()
                # return false

        # if (bytes == 1):
                # for x in range(0, 8):
                        # b[x] = ord(b[x][0]) << 24;
        # if (bytes == 2):
                # for x in range(0, 8):
                        # b[x] = ord(b[x][0]) << 24 | ord(b[x][1]) << 16;
        # if (bytes == 4):
                # pass

        return b


# gets the data from the fm2 dataline and returns as 2player bitfield
def fm2_getbits(fm2_str):
        p1 = 0
        p2 = 0

        if (len(fm2_str) == 0):
                cleanup()
                return 0, 0

        data = fm2_str.split('|')

        for x in range(0, 8):
                p1 = p1 | (0 if (data[2][x] == '.') else (1 << x))
                if (len(data[3])):
                        p2 = p2 | (0 if (data[3][x] == '.') else (1 << x))

        return (p1 << 24), (p2 << 24)

def open_next_file():
  global fh
  global filecount

  fh.close()
  filecount += 1
  if (len(sys.argv) < 3 + filecount):
    sys.exit(0)
          
  fh = open(sys.argv[2+filecount], 'r')
        
def get_next_line():
  global fh
  
  while (True):
    fbuf = fh.readline()
    
    if (not fbuf):
      open_next_file()
    elif (fbuf[0:1] == "#"):
      pass
    else:
      return fbuf
  
# reads the next input and returns appropriately formatted data
def send_next_frame(is_reset):
        
        fbuf = get_next_line()
            
        if (int(fbuf[24:25]) == 1):
            print "c Y %0.3X" % (int(fbuf[16:19]) * 16) + " " + "%0.3X" % (int(fbuf[20:23]) * 16 + 512) + " f";
            ser.write("c Y %0.3X" % (int(fbuf[16:19]) * 16) + " " + "%0.3X" % (int(fbuf[20:23]) * 16 + 512) + " f")
        else:
            print "c N f";
            ser.write("c N f")
        return

# send the first 20 frames
for i in range(1,20):
  send_next_frame(0)
        
print("")

while (1):
        while (ser.inWaiting() == 0):
                pass

        c = ser.read()

        if (c == 'f'):
                framecount += 1
                send_next_frame(0)

        #printinfo()
