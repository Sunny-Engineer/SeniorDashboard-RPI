from time import sleep
import time
import datetime
import os
import subprocess
# import struct
import sys
import json
import glob

#
#  This script runs once per minute and checks to see if there is a new dashboard to display.
#

try:
    sysargv = sys.argv[1]
except:
    sysargv = ''

#configure Variables
cf = {}  # configuration file
firsttime = 'yes'
last_minute = 99
logf = {} # - Looks unused?
now = datetime.datetime.now()
testteller = 0
now_playing = ''

# display the system number on the screen
os.system('sudo mkdir /dev/shm/temp && sudo mkdir /dev/shm/web && sudo chmod 777 -R /dev/shm')

txt_screen1 = '<html><head><meta http-equiv="refresh" content="2"></head><body bgcolor=white><font color=black>'
txt_screen1 += '<table width=100%><tr><td width=20%>&nbsp;<td widht=60% valign=top>'
txt_screen1 += '<p style=\'font-family: "Arial Black", Gadget, sans-serif; font-size: 40px; color:#000000\'><br><br>'
txt_screen1 += '<td width=20% valign=top><p style=\'font-family: "Arial Black", Gadget, sans-serif; font-size: 40px; color:#000000\'>99:99'

txt_screen2 = '</table></body></html>'

# open the index.html file and write the time into the html.
try:
    f = open('/dev/shm/web/index.html', 'w')
    f.write(txt_screen1.replace('99:99',now.strftime("%I:%M %p")) + txt_screen2)
    f.close()
except Exception as e:
    print ("The error = " + str(e))

# define functions
def addtopermlog (sstr):
    # Write to operation log "/home/pi/log.txt" - Unused???
    now = datetime.datetime.now()

    try:
        with open("/home/pi/log.txt", 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            sstr = now.strftime("%Y %m %d %H:%M ") + sstr + '\n' + content
            sstr = sstr[:1200]
            f.write(sstr)
    except:
        f = open("/home/pi/log.txt", 'a')
        f.write(now.strftime("%Y %m %d %H:%M ") + sstr)
    f.close()

def addtosessionlog(sstr):
    # Writes to Session log "/home/shm/log.txt"  unused???
    now = datetime.datetime.now()
    try:
        with open("/dev/shm/log.txt", 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(now.strftime("%Y %m %d %H:%M ") + sstr + '\n' + content)
    except:
        f = open("/dev/shm/log.txt", 'a')
        f.write(now.strftime("%Y %m %d %H:%M ") + sstr)
    f.close()

def computernr():
    # read the computer number and return
    with open('/proc/cpuinfo') as f:
        for line in f:
            line = line.replace('\n', '', 1)
            line = line.replace('\r', '', 1)
            if line[:6] == 'Serial':
                computernr = line[12:]

    # Strip off all leading zeros
    while computernr[:1] == '0':
        computernr = computernr[1:]

    return computernr

def read(kkey):
    # read a configuration key from file.
    if kkey in cf:
        return cf.get(kkey)
    else:
        return ''

def readconfigtxt():
    # read the config file, and if it is missing, read configres and set global variable.
    global cf

    f = open('/home/pi/config.txt', 'r')
    sstr = f.read()
    if len(sstr) < 5:
        f.close()
        f = open('/home/pi/configres.txt', 'r')
        sstr = f.read()
    cf = json.loads(sstr)
    f.close()

# Start Process Here 
readconfigtxt()
read_configtxt_hour = now.strftime("%H")

ssstring = ''

ps = subprocess.Popen(['sudo','iwlist','wlan0','scan'], stdout=subprocess.PIPE).communicate()[0]
processes = ps.split('\n')

# Get a list of processes, and look for essid process.  NOt sure what is happening here
for row in processes:
    sstring = str(row)
    tteller =  sstring.find('ESSID')
    if tteller > 0:
        sstring = sstring[tteller:]
        sstring = sstring.replace('"','')
        sstring = sstring.replace('ESSID:','')
    if ssstring == '':
        ssstring = sstring
    else:
        ssstring = ssstring + '\n' + sstring

# write the wifi name to the log file
try:
    wifinet = open('/dev/shm/wifinet.txt', 'w')
    wifinet.write(ssstring)
    wifinet.close()
except Exception as e:
    print('Write Wifi Failed - ')

processisrunning = 'I dont know'
ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
processes = ps.split('\n')

os.system('sudo chmod 777 /dev/tt*')

for row in processes:
    sstring = str(row)
    if 'xinit' in sstring:
        processisrunning = 'yes'

# start chromium browser
if processisrunning != 'yes':
#   os.system('xinit /home/pi/f.sh &')
    print('starten' + str(os.system('sudo -u pi xinit /home/pi/f.sh >/dev/null 2>&1 &')))
else:
    print ('don\'t start xinit with f.sh')

while testteller < 9:
  #if customer number = 0, write the cpu number on the screen
    if read('customernr') == 0:
        f = open('/dev/shm/web/index.html', 'w')
        sstr = '<tr><td><td colspan=2><p style=\'font-family: "Arial Black", Gadget, sans-serif; font-size: 40px; color:#000000\'>'
        sstr += 'Please contact the servicedesk:<br>Tel 012 345 6789<br><br>Your computernumber: ' + computernr()
        print ('cust222' + sstr)
        f.write(txt_screen1.replace('99:99',now.strftime("%I:%M %p")) + sstr + txt_screen2)
        f.close()
        sleep(15)
        readconfigtxt()
    else:
        while last_minute == now.minute:
            sleep(1)
            now = datetime.datetime.now()
        last_minute = now.minute
        # returns a list of zip files
        present = glob.glob("/var/www/*.zip")
        print ('lm:' + str(last_minute) + ' ' + str(now.minute))

        # Turn off the display file by setting values to ""
        now_playing_night = ''
        now_playing_alarm = ''
        now_playing_normal = ''

        # loop through all files to find the one that should display.
        for ffile in present:
            # see if the file is a night file, and process
            if ffile[:14] == '/var/www/night':
                # Get the file name from the path position 15 + which should be the night 'Time"
                sstr = ffile[14:]
                # get the 12 digit time from the file name
                sstr = sstr[:12]
                # if the name time is less than the current time and the file  is greater than then currently displaying night file, set the now playing night file to the current file.
                if sstr < time.strftime("%Y%m%d%H%M") and ffile > now_playing_night:
                    now_playing_night = ffile

      # see if the file is a normal file, and process
            if ffile[:15] == '/var/www/normal':
                sstr = ffile[15:]
                sstr = sstr[:12]
                if sstr < time.strftime("%Y%m%d%H%M") and ffile > now_playing_normal:
                    now_playing_normal = ffile

            # see if the file is an alarm file, and process
            if ffile[:14] == '/var/www/alarm':
                sstr = ffile[14:]
                sstr = sstr[:12]
                thirty_min_ago = datetime.datetime.now() - datetime.timedelta(minutes=30)
                thirty_min_ago = thirty_min_ago.strftime("%Y%m%d%H%M")
                if sstr < time.strftime("%Y%m%d%H%M") and sstr > thirty_min_ago and ffile > now_playing_alarm:
                    now_playing_alarm = ffile

        # now print something somewhere...
        print ('spal:' + now_playing_alarm)
        print ('spni:' + now_playing_night)
        print ('spno:' + now_playing_normal)

        # determine if it is night...
        it_is_night = False
        time_now = int(now.strftime("%H%M"))

        # read the night start time from the config file.
        if read('night_start') == '':
            night_start = -1
        else:
            night_start = int(cf['night_start'])

        # read the night end time from the config file.
        if read('night_end') == '':
            night_end = -1
        else:
            night_end = int(cf['night_end'])

        # if the
        if night_start != -1 and night_end != -1:
            if night_start > night_end and (night_start < time_now or night_end > time_now):
                it_is_night = True
            if night_start < night_end and (night_start < time_now and night_end > time_now):
                it_is_night = True

	    # if an alarm should be playing, set the
        if now_playing_alarm != '':
            should_play = now_playing_alarm
        elif it_is_night:
            should_play = now_playing_night
        else:
            should_play = now_playing_normal


        print( 'should play:' + should_play + ' now playing:' + now_playing)

        # If the file currently playing is not the newly scheduled file...
        if now_playing != should_play:

            # remove all existing files from /dev/shm/temp/*.*
            os.system('sudo rm /dev/shm/temp/* &')
            sleep(1)
            #Then unzip the new display html to the same directory
            os.system('sudo unzip -o ' + should_play + ' -d /dev/shm/temp')

            # If there is a clock html file, open it, read the data and then delete it.
            if os.path.isfile('/dev/shm/temp/clock.html'):
                f = open('/dev/shm/temp/clock.html', 'r')
                clock_source = f.read()
                os.system('sudo rm /dev/shm/temp/clock.html')
            else:
                clock_source = ''
 
 # if there is not clock file, create one.
if clock_source != '':
      f = open('/dev/shm/web/clock.html', 'w')
      f.write(clock_source.replace('99:99',now.strftime("%I:%M %p")))
      f.close()

# if there is a new file to display, copy the temp directory to the /dev/shm/web, and then run the refresh script which essentially forces the browser to refresh and read the new files.
if now_playing != should_play:
    now_playing = should_play
    os.system('sudo cp /dev/shm/temp/* /dev/shm/web && sudo /home/pi/refresh.sh')
	  
    now = datetime.datetime.now()
    tteller += 1
  
if sysargv == 'test':
    testteller += 1

if read_configtxt_hour != now.strftime("%H"):
    read_configtxt_hour = now.strftime("%H")
    readconfigtxt()

print ('my first sony')