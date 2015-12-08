import os
import serial
import sys
import time

baud = 9600
prebuffer = 30
timeout = 0

framecount = 0

frame_data = [];

enter_movie = "time_menu_enter.dsm"
exit_movie = "time_menu_exit.dsm"

if len(sys.argv) < 6:
        sys.stderr.write('Usage: ' + sys.argv[0] + ' <interface> <desired_hour> <desired_minute> <current_hour> <current_minute>\n\n')
        sys.exit(0)

if not os.path.exists(enter_movie):
        sys.stderr.write('Error: "' + enter_movie + '" not found\n')
        sys.exit(1)
        
if not os.path.exists(exit_movie):
        sys.stderr.write('Error: "' + exit_movie + '" not found\n')
        sys.exit(1)
        
def decode_dsm_to_serial(line):
    if (int(line[24:25]) == 1):
        return "c Y %0.3X" % (int(line[16:19]) * 16) + " " + "%0.3X" % (int(line[20:23]) * 16 + 512) + " f"
    else:
        return "c N f"
        
# open the file and get the extension
fh = open(enter_movie, 'r')
while True:
    line = fh.readline()
    if not line:
        break

    frame_data.append(decode_dsm_to_serial(line))
fh.close()

desired_hour = int(sys.argv[2])
desired_minute = int(sys.argv[3])
current_hour = int(sys.argv[4])
current_minute = int(sys.argv[5])

hour_delta = 0;

if (desired_hour > current_hour):
    hour_delta = desired_hour - current_hour
    if (hour_delta > 12):
        hour_delta = -((current_hour + 24) - desired_hour)
else:
    hour_delta = desired_hour - current_hour
    if (hour_delta < -12):
        hour_delta = -((current_hour - 24) - desired_hour)
    
if (hour_delta > 0):
    for i in range(0,hour_delta):
        frame_data.append(decode_dsm_to_serial("|0|.............088 047 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............088 047 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............000 000 0|"))
else:
    for i in range(0,-hour_delta):
        frame_data.append(decode_dsm_to_serial("|0|.............088 128 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............088 128 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............000 000 0|"))

minute_delta = 0;

if (desired_minute > current_minute):
    minute_delta = desired_minute - current_minute
    if (minute_delta > 30):
        minute_delta = -((current_minute + 60) - desired_minute)
else:
    minute_delta = desired_minute - current_minute
    if (minute_delta < -30):
        minute_delta = -((current_minute - 60) - desired_minute)
    
if (minute_delta > 0):
    for i in range(0,minute_delta):
        frame_data.append(decode_dsm_to_serial("|0|.............168 047 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............168 047 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............000 000 0|"))
else:
    for i in range(0,-minute_delta):
        frame_data.append(decode_dsm_to_serial("|0|.............168 128 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............168 128 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............000 000 0|"))


fh = open(exit_movie, 'r')
while True:
    line = fh.readline()
    if not line:
        break

    frame_data.append(decode_dsm_to_serial(line))
fh.close()       

ser = serial.Serial(sys.argv[1], baud, timeout = 0)

# reads the next input and returns appropriately formatted data
def send_next_frame(is_reset):
    global framecount

    print frame_data[framecount];
    ser.write(frame_data[framecount])

    framecount += 1
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
        send_next_frame(0)
        if (framecount == len(frame_data)):
            sys.exit(0)
