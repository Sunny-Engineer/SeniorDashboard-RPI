# my first python
from time import sleep
import os.path, time
import os
import datetime
import subprocess
import urllib
import urllib2
import sys
import glob
import commands
from random import randint
import json
try:
  sysargv = sys.argv[1]
except:
  sysargv = ''

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

logf = {}
cf = {}
sstr = subprocess.Popen(['date'], stdout=subprocess.PIPE).communicate()[0]
sstr = sstr.split(' ')
currenttimezone = sstr[5]
if is_number(currenttimezone):
  currenttimezone = sstr[4]
else:
  currenttimezone = 0
editconfigtxt = ''
newtimezone = ''
os.system('sudo mkdir /dev/shm/a &')
os.system('sudo mkdir /dev/shm/web &')
os.system('sudo chmod 777 -R /dev/shm')
present = glob.glob("/home/pi/*.zip")

sstr = commands.getoutput('date')
sstr = sstr.split(' ')
currenttimezone = sstr[4]

def addtopermlog (sstr):
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

def addtosessionlog (sstr):
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
  print sstr

def messagetoserver(sstr):
  f = open('/dev/shm/messagetoserver.txt', 'a')
  sstr = sstr.replace(' ', '_')
  f.write('_' + sstr)
  f.close()

def read(ssleutel):
  if ssleutel in cf:
    return cf.get(ssleutel)
  else:
    return ''
    
def readanswer(ssleutel):
  if ssleutel in answer:
    return answer.get(ssleutel)
  else:
    return ''

def save_config(cf):
  f = open('/home/pi/config.txt', 'w')
  f.write(json.dumps(cf))
  f.close()

try:
  now = datetime.datetime.now()
  procesloopt = 'weet niet'
  ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
  processes = ps.split('\n')
  for row in processes:
    sstring = str(row)
    if 'python /home/pi/a.py' in sstring:
      procesloopt = 'yes'
  if procesloopt != 'yes':
    os.system('cd /home/pi && sudo python /home/pi/a.py &')
    addtopermlog('mainprocess a.py started')
    print 'I ll start the main program'
  else:
    print 'dont start the main program: it is running already'
  # read config.txt
  f = open('/home/pi/config.txt', 'r')
  sstr = f.read()
  if len(sstr) < 5:
    f.close()
    f = open('/home/pi/configres.txt', 'r')
    sstr = f.read()
  print 'str config:' + sstr
  cf = json.loads(sstr)
  f.close()
except:
  print 'something wrong starting a.py or reading config.txt'

# find ip address
ipaddress = ''
ps = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE).communicate()[0]
processes = ps.split('\n')
next_is = ''
for row in processes:
  sstr = str(row)
  print sstr
  if 'eth0' in sstr:
    next_is = 'eth0'
  if 'ppp' in sstr:
    next_is = 'ppp'
  if 'wlan0' in sstr:
    next_is = 'wlan0'
  t = sstr.find('inet ')
  if t > 0 and not '127.0.0.1' in sstr:
    sstr = sstr[t + 5:]
    sstr = sstr[:15]
    t = sstr.find(' ')
    if t > 0:
      sstr = sstr[:t]
    if ipaddress != '':
      ipaddress += '_'
    ipaddress += next_is + '_' + sstr
    next_is = ''
    print 'ipaddress: ' + ipaddress

# generate random number based on the computernumber
with open('/proc/cpuinfo') as f:
  for line in f:
    line = line.replace('\n', '', 1)
    line = line.replace('\r', '', 1)
    if line[:6] == 'Serial':
      computernr = line[12:]
tteller = 0
ccomputernr = ''
while tteller < len(computernr):
  if is_number(computernr[tteller:tteller+1]):
    ccomputernr += computernr[tteller:tteller+1]
  tteller += 1
tteller = int(ccomputernr)
while tteller > 3359:
  tteller = tteller - 3360
randomizer = round(tteller/60-0.5 +3)
print 'randomizer:', str(randomizer)

if sysargv == 'test' or tteller%60 == now.minute:
  if sysargv == '':
    sstr = randint(0, 59)
    print 'sleep a ' + str(sstr)
    sleep(sstr)
  if now.hour == 11:
    os.system("sudo python /home/pi/update.py Doug &")
    addtosessionlog('checking new software')
    os.system("sudo cp /home/pi/config.txt /home/pi/configres.txt &")

if os.path.isfile('/dev/shm/back_to_wifi'):
  f = open('/dev/shm/back_to_wifi', 'r')
  back_to_wifi = f.readline()
  f.close()
  print 't:' + str(time.time()) + ' b:' + back_to_wifi
  back_to_wifi = float(back_to_wifi)
  print 'time now    : ' + str(time.time())
  print 'back to wifi: ' + str(back_to_wifi)
  if float(time.time()) > float(back_to_wifi):
    addtosessionlog('m.py will disconnected. Time: ' + str(time.time()) + ' back_to_wifi:' + str(back_to_wifi))
    os.system('sudo /home/pi/sakis3g disconnect')
    os.system('sudo ip link set wlan0 down && sudo ip link set eth0 down && sudo ip link set wlan0 up && sudo ip link set eth0 up')
    f = open("/dev/shm/back_to_wifi", 'w')
    f.write(str(2541628978))   # 17 juli 2050
    f.close()
    back_to_wifi = 2541628979
    print 'btw0:' +str(back_to_wifi)
else:
  f = open("/dev/shm/back_to_wifi", 'w')
  f.write(str(2541628980))   # 17 juli 2050
  f.close()
  back_to_wifi = 2541628981
  print 'btw1:' +str(back_to_wifi)

# hhh controlere of t echt gescreven is:
f = open('/dev/shm/back_to_wifi', 'r')
addtosessionlog('written back to wifi:' + f.readline())
f.close()

# every x seconds retrieve new contents
f = read('frequency')
if not is_number(f) or float(f) < 300:
  f = 300
f = int(f/60)
if f > 1339:
  f = 1339
randomnr = int(ccomputernr) + 60* int(now.strftime("%H")) + int(now.strftime("%M")) 
addtosessionlog('frequency:' + str(f) +' randomnr:' + str(randomnr) + ' remainder:' + str(randomnr % f))

if sysargv == '' and randomnr % f < 1 :
  sstr = randint(0, 59)
  print 'sleep b ' + str(sstr)
  sleep(sstr)
if sysargv == 'test1' or randomnr % f < 1 :
  if os.path.isfile('/dev/shm/messagetoserver.txt'):
    f = open('/dev/shm/messagetoserver.txt', 'r')
    mmessagetoserver = f.readline()
    f.close()
    os.system('sudo rm /dev/shm/messagetoserver.txt &')
  else:
    mmessagetoserver = ''
  url_str = '/n.php?c=' + computernr + '&i=' + ipaddress + '&v=' + read('version') + mmessagetoserver.replace(' ', '_')
  url_str = read('ourserver') + url_str
  print 'url_str:' + url_str
#   if False:
  try:
    sstr = 'cd /tmp && wget -N --tries=3 "'+ url_str + '"'
    addtosessionlog('retrieving using: ' + sstr)
    os.system(sstr)
    sleep(3)
  except:
    addtosessionlog('cannt get the data via wifi')
  try:
    tteller = 0
    os.system('sudo mv /tmp/n* /tmp/a.txt')
    f = open("/tmp/a.txt", 'r')
    sstr = f.read()
    os.system('sudo rm /tmp/a* ')
    print sstr
    addtosessionlog(sstr)
    answer = json.loads(sstr)
#   else:
  except:
    addtosessionlog('we start gsm connection. No wifi and no wired connection.')
    if read('sim_apn') == '':
      back_to_wifi = time.time() + 68400 # one day
      sim_apn = 'soracom.io'
      sim_user = 'sora'
      sim_pw = 'sora'
    else:
      back_to_wifi = time.time() + 3600 # one houre
      sim_apn = read('sim_apn')
      sim_user = read('sim_user')
      sim_pw = read('sim_pw')
# sudo /home/pi/sakis3g "connect" "--pppd" "APN=internet" "BAUD=9600" OTHER="CUSTOM_TTY" CUSTOM_TTY="/dev/ttyAMA0" "APN_USER=" "APN_PASS=" "SIM_PIN="
    sstr = 'sudo /home/pi/sakis3g "connect" "--pppd" "APN=' + sim_apn + '" "BAUD=9600" OTHER="CUSTOM_TTY" CUSTOM_TTY="/dev/ttyAMA0" '
    sstr += '"APN_USER=' + sim_user + '" "APN_PASS=' + sim_pw + '" "SIM_PIN="'
    sstr = os.system(sstr)
    addtosessionlog('connected' + str(sstr) + ' back_to_wifi:' + str(back_to_wifi))
    f = open("/dev/shm/back_to_wifi", 'w')
    f.write(str(back_to_wifi))
    f.close()
    print 'btw2:' +str(back_to_wifi)
    sstr = 'cd /tmp && wget -N --tries=3 "'+ url_str + '"'
    os.system(sstr)
    sleep(3)
    tteller = 0
    os.system('sudo mv /tmp/n* /tmp/a.txt')
    f = open("/tmp/a.txt", 'r')
    sstr = f.read()
    addtosessionlog('json from server: ' + sstr)
    answer = json.loads(sstr)
    addtosessionlog('succesfully contacted the server')
#   if True:
  try:
    if read('customernr') != readanswer('customernr'):
      cf['customernr'] = readanswer('customernr')
      save_config(cf)
    if read('frequency') != readanswer('frequency'):
      cf['frequency'] = readanswer('frequency')
      save_config(cf)
    if read('night_start') != readanswer('night_start'):
      cf['night_start'] = readanswer('night_start')
      save_config(cf)
    if read('night_end') != readanswer('night_end'):
      cf['night_end'] = readanswer('night_end')
      save_config(cf)
    if readanswer('SSID') != '':
      ssid = readanswer('SSID')
      networkpassword = readanswer('networkpassword')
      if len(networkpassword) > 0 and len(networkpassword) < 8:
        messagetoserver('Invalid password found: ' + networkpassword + '.')
      else:
        found_ssid = 'no'
        ssidknown = 'no'
        new_wpa_suppl = ''
        write_new_wpa_suppl = 'no'
        f = open( "/etc/wpa_supplicant/wpa_supplicant.conf", "r" )
        for string in f:
          if string[0:-1] == "  ssid=\"" + ssid +"\"":
            found_ssid = 'yes'
            ssidknown = 'yes'
            new_wpa_suppl += string + "  scan_ssid=1\n"
          elif ssidknown == 'yes' and ((string[:6] == "  psk=" and string[0:-1] != "  psk=\"" + networkpassword +"\"") or (string[0:-1] == "  key_mgmt=NONE" and networkpassword != '')):
            # here we know we are reading the line of the password
            if networkpassword == '':
              new_wpa_suppl += "  key_mgmt=NONE\n"
            else:
              new_wpa_suppl += "  psk=\"" + networkpassword +"\"\n"
            ssidknown = 'no'
            write_new_wpa_suppl = 'yes'
            addtosessionlog('Change wifi network credentials.')
          elif string[0:11] != "  scan_ssid" and string[0:-1] != '':
            new_wpa_suppl += string
        if found_ssid == 'no':
          # obviously there is a new SSID
          new_wpa_suppl += "network={\n";
          new_wpa_suppl += "  ssid=\"" + ssid + "\"\n  scan_ssid=1\n";
          if networkpassword != '':
            new_wpa_suppl += "  psk=\"" + networkpassword + "\"\n}\n";
          else:
            new_wpa_suppl += "  key_mgmt=NONE\n}\n";
          write_new_wpa_suppl = 'yes'
          addtosessionlog('Wifi network added.')
        if write_new_wpa_suppl == 'yes':
  #             f = open( "/etc/wpa_supplicant/wpa_supplicant.conf", "r" )
          f = open('/tmp/wpa_s', 'w')
          f.write(new_wpa_suppl)
          f.close()
          os.system('sudo cp /tmp/wpa_s /etc/wpa_supplicant/wpa_supplicant.conf');
          messagetoserver('Wifi credentials updated')
    if readanswer('timezone') != '':
      print 'currenttimezone:', currenttimezone
      if readanswer('timezone') == 0:
        timezoneshouldbe = 'EDT'
      elif readanswer('timezone') == -1:
        timezoneshouldbe = 'CDT'
      elif readanswer('timezone') == -2:
        timezoneshouldbe = 'MDT'
      elif readanswer('timezone') == -3:
        timezoneshouldbe = 'PDT'
      elif readanswer('timezone') == -4:
        timezoneshouldbe = 'AKDT'
      elif readanswer('timezone') == -5:
        timezoneshouldbe = 'HDT'
      else:
        timezoneshouldbe = 'HST'
      if timezoneshouldbe != currenttimezone:
        if readanswer('timezone') == '0':
          newtimezone = 'New_York'
        elif readanswer('timezone') == '-1':
          newtimezone = 'Chicago'
        elif readanswer('timezone') == '-2':
          newtimezone = 'Denver'
        elif readanswer('timezone') == '-3':
          newtimezone = 'Los_Angeles'
        elif readanswer('timezone') == '-4':
          newtimezone = 'Anchorage'
        elif readanswer('timezone') == '-5':
          newtimezone = 'Adak'
        else:
          newtimezone = 'Honolulu'
    for zipfile in readanswer('zipfiles'):
      if zipfile not in present:
        sstr = 'cd /var/www && wget -N --tries=3 "' + read('ourserver') + '/' + str(read('customernr')) + '/' + zipfile +'"'
        os.system(sstr)
        print('wget:' + sstr)
  except:
    addtopermlog('I didnt receive a valid answer from the server.')

# clean /var/www:
if (now.hour == 12 and now.minute == 12) or sysargv == 'test2':
# hhh delete old files
# check that the files are really there:
  present = glob.glob("/var/www/*.zip")
  now_playing_night = '/var/www/night'
  now_playing_alarm = '/var/www/alarm'
  now_playing_normal = '/var/www/normal'
  for ffile in present:
    if ffile[:14] == '/var/www/night':
      sstr = ffile[14:]
      sstr = sstr[:12]
      if sstr < time.strftime("%Y%m%d%H%M") and ffile > now_playing_night:
        now_playing_night = ffile
    if ffile[:15] == '/var/www/normal':
      sstr = ffile[15:]
      sstr = sstr[:12]
      if sstr < time.strftime("%Y%m%d%H%M") and ffile > now_playing_normal:
        now_playing_normal = ffile
    if ffile[:14] == '/var/www/alarm':
      sstr = ffile[14:]
      sstr = sstr[:12]
      if sstr < time.strftime("%Y%m%d%H%M") and ffile > now_playing_alarm:
        now_playing_alarm = ffile
  for ffile in present:
    if ffile[:14] == '/var/www/night' and ffile < now_playing_night:
      os.system('sudo rm /home/pi/' + ffile + ' &')
    if ffile[:15] == '/var/www/normal' and ffile < now_playing_normal:
      os.system('sudo rm /home/pi/' + ffile + ' &')
    if ffile[:14] == '/var/www/alarm' and ffile < now_playing_alarm:
      os.system('sudo rm /home/pi/' + ffile + ' &')

if now.hour == 5 and now.minute == 0:
  os.system('sudo rm /dev/shm/log* &')

# messagetoserver('sstr')
if newtimezone != '':
  if newtimezone == 'Honolulu':
    os.system('sudo cp /usr/share/zoneinfo/Pacific/Honolulu /etc/localtime')
  else:
    sstr = 'sudo cp /usr/share/zoneinfo/America/' + newtimezone + ' /etc/localtime'
    print sstr
    os.system(sstr)
  messagetoserver('New timezone: ' + newtimezone)

try:
  now = datetime.datetime.now()
  procesloopt = 'weet niet'
  ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
  processes = ps.split('\n')
  for row in processes:
    sstring = str(row)
    if 'python /home/pi/a.py' in sstring:
      procesloopt = 'yes'
  if procesloopt != 'yes':
    os.system('cd /home/pi && sudo python /home/pi/a.py &')
except:
  print 'STILL NO GOOD START'

print('my first sony' + str(now.minute+100*now.hour))





