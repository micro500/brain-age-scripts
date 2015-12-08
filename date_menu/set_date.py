import os
import serial
import sys
import time

baud = 9600
prebuffer = 30
timeout = 0

framecount = 0

frame_data = [];

enter_movie = "date_menu_enter.dsm"
exit_movie = "date_menu_exit.dsm"

if len(sys.argv) < 6:
        sys.stderr.write('Usage: ' + sys.argv[0] + ' <interface> <desired_month> <desired_day> <desired_year> <current_month> <current_day> <current_year>\n\n')
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

# Year down
# |0|.............191 128 1|
# |0|.............191 128 1|
# |0|.............191 128 1|
# |0|.............000 000 0|

# Year up
# |0|.............191 047 1|
# |0|.............191 047 1|
# |0|.............191 047 1|
# |0|.............000 000 0|

# day down
# |0|.............104 128 1|
# |0|.............104 128 1|
# |0|.............104 128 1|
# |0|.............000 000 0|

# day up
# |0|.............104 047 1|
# |0|.............104 047 1|
# |0|.............104 047 1|
# |0|.............000 000 0|

# month down
# |0|.............040 128 1|
# |0|.............040 128 1|
# |0|.............040 128 1|
# |0|.............000 000 0|

# month up
# |0|.............040 047 1|
# |0|.............040 047 1|
# |0|.............040 047 1|
# |0|.............000 000 0|

desired_month = int(sys.argv[2])
desired_day = int(sys.argv[3])
desired_year = int(sys.argv[4])
current_month = int(sys.argv[5])
current_day = int(sys.argv[6])
current_year = int(sys.argv[7])

# bring the day to 1
for i in range(0,current_day - 1):
    frame_data.append(decode_dsm_to_serial("|0|.............104 128 1|"))
    frame_data.append(decode_dsm_to_serial("|0|.............104 128 1|"))
    frame_data.append(decode_dsm_to_serial("|0|.............000 000 0|"))

month_delta = 0;

if (desired_month > current_month):
    month_delta = desired_month - current_month
    if (month_delta > 6):
        month_delta = -((current_month + 12) - desired_month)
else:
    month_delta = desired_month - current_month
    if (month_delta < -6):
        month_delta = -((current_month - 12) - desired_month)
    
if (month_delta > 0):
    for i in range(0,month_delta):
        frame_data.append(decode_dsm_to_serial("|0|.............040 047 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............040 047 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............000 000 0|"))
else:
    for i in range(0,-month_delta):
        frame_data.append(decode_dsm_to_serial("|0|.............040 128 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............040 128 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............000 000 0|"))


for i in range(0,desired_day - 1):
    frame_data.append(decode_dsm_to_serial("|0|.............104 047 1|"))
    frame_data.append(decode_dsm_to_serial("|0|.............104 047 1|"))
    frame_data.append(decode_dsm_to_serial("|0|.............000 000 0|"))
        
        
year_delta = 0;

if (desired_year > current_year):
    year_delta = desired_year - current_year
    if (year_delta > 50):
        year_delta = -((current_year + 60) - desired_year)
else:
    year_delta = desired_year - current_year
    if (year_delta < -50):
        year_delta = -((current_year - 60) - desired_year)
    
if (year_delta > 0):
    for i in range(0,year_delta):
        frame_data.append(decode_dsm_to_serial("|0|.............191 047 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............191 047 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............000 000 0|"))
else:
    for i in range(0,-year_delta):
        frame_data.append(decode_dsm_to_serial("|0|.............191 128 1|"))
        frame_data.append(decode_dsm_to_serial("|0|.............191 128 1|"))
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
