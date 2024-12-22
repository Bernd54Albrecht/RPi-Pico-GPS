# Raspberry Pi Pico and GPS ublox NEO-6M or NEO-7M
# receive data via UART1 (Tx=GP4, RX=GP5)
# based on Module micropyGPS by Michael Calvin McCoy
# download and save in sub-directory /lib
# https://github.com/inmcm/micropyGPS/blob/master/micropyGPS.py
# LCD line 1: date and time from GPS
# LCD line 2: present position
# LCD line 3: waypoint
# LCD line 4: true course and distance to waypoint

from machine import UART, I2C, Pin
from time import sleep, sleep_ms, ticks_ms
from keypad import Keypad
from micropyGPS import MicropyGPS
from machine_i2c_lcd import I2cLcd
from math import cos, radians, degrees, atan2, sqrt

# Instantiate the micropyGPS object
gps = MicropyGPS()

# Instantiate the UART object 
gps_serial = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

# Interim Waypoint  Elbphilharmonie, change to your favorite position
latDDWP = 53
latMMmmmmWP = 32.5001
latNSWP = "N"
lonDDWP = 9
lonMMmmmmWP = 59.0001
lonEWWP = "E"

# Instantiate LCD2004 with I2C-Adapter
# The PCF8574 has a jumper selectable address: 0x20 - 0x27
DEFAULT_I2C_ADDR = 0x27
# On the RPi Pico, I2C0 shows up on GP0 (sda) and GP1 (scl)
i2c = I2C(0, sda=0, scl=1, freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 4, 20)
lcd.putstr("Press * to enter waypoint")
sleep(3)
lcd.clear()

# Define GPIO pins for rows
row_pins = [Pin(6),Pin(7),Pin(8),Pin(9)]

# Define GPIO pins for columns
column_pins = [Pin(10),Pin(11),Pin(12),Pin(13)]

# Define keypad layout
keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']]

keypad = Keypad(row_pins, column_pins, keys)

def keyInput():
    key_pressed = 0
    keyList = []
    for n in range(20):
        keyList.append("1")
    keyString = ""
    i = 0

    while i<20:
        key_pressed = keypad.read_keypad()
        if key_pressed:
            print("Key pressed:", key_pressed)
            keyList[i] = key_pressed
            if keyList[i] == 'D':
                i = i - 1
            else:
                i +=1
            print("keyList:", keyList[0:i])
            lcd.move_to(0, 0)
            lcd.clear()
            lcd.putstr(keyList[0:i])
        sleep(0.2)  # debounce and delay
    sleep(0.5)	# little delay for stability
    return keyList    

# self-defined function for better presentation of the time String
def timeString(timeUTC):
    hour = timeUTC[0]
    if (hour<10):
        hour = "0"+str(hour)
    else:
        hour = str(hour)
    minute = timeUTC[1]
    if (minute<10):
        minute = "0"+str(minute)
    else:
        minute = str(minute)                    
    second = int(timeUTC[2])
    if (second<10):
        second = "0"+str(second)
    else:
        second = str(second)
    return hour + ":" + minute + ":" + second

# self-defined function for better presentation of the date
def dateString(dateShort):
    dateList = dateShort.split("/")
    day = dateList[1]
    month = dateList[0]    
    year = dateList[2]
    return day + "." + month + ".20" + year

# self-defined function for better presentation of the latitude
def latString(latitude):
    global latDD, latMMmmmm, latNS, latPrint, latLCD
    latList = latitude.split("°")
    latDD = latList[0]
    latList2 = latList[1].split("'")
    latMMmmmm = latList2[0][:-1]	# delete last digit
    latNS = latList2[1]		# north or south (
    latPrint = latDD.strip()+"°"+ latMMmmmm.strip()+"'"+ latNS.strip()
    latLCD = latDD.strip()+latMMmmmm.strip()+latNS.strip()
    return

# self-defined function for better presentation of the longitude
def lonString(longitude):
    global lonDD, lonMMmmmm, lonEW, lonPrint, lonLCD
    lonList = longitude.split("°")
    lonDD = lonList[0]
#     if int(lonDD) < 100:
#         lonDDD = "0"+lonDD
    if int(lonDD) < 10:
        lonDD = "0"+lonDD                    
    lonList2 = lonList[1].split("'")
    lonMMmmmm = lonList2[0][:-1]	# delete last digit
    lonEW = lonList2[1].strip()
    lonPrint = lonDD.strip()+"°"+ lonMMmmmm.strip()+"'"+ lonEW.strip()
    lonLCD = lonDD.strip() + lonMMmmmm.strip() + lonEW
    return

# self-defined function for input of waypoint coordinates
def enterWP():
    global latDDWP, latMMmmmmWP, lonDDWP, lonMMmmmmWP, lonEWWP
    print("Enter Waypoint")
    lcd.clear()
    lcd.move_to(0, 2)
    lcd.putstr("Enter Waypoint")
    sleep(0.5)
    keyList = keyInput()
    print(keyList)
    latDDWP = int(keyList[0]+keyList[1])
    latMMWP = int(keyList[2]+keyList[3])
    latmmmmWP = float(keyList[5]+keyList[6]+keyList[7]+keyList[8])/(10000)
    latMMmmmmWP = latMMWP + latmmmmWP
    lonDDWP = int(keyList[10]+keyList[11])
    lonMMWP = int(keyList[12]+keyList[13])
    lonmmmmWP = float(keyList[15]+keyList[16]+keyList[17]+keyList[18])/(10000)
    lonMMmmmmWP = lonMMWP + lonmmmmWP
    if keyList[19] == 'B':
        lonEWWP = "E"
    elif keyList[19] == 'C':
        lonEWWP = "W"
    print(latDDWP,"°",latMMmmmmWP,"'N",lonDDWP,"°",lonMMmmmmWP,"'",lonEWWP)
    lcd.clear()
    lcd.move_to(0, 2)            
    lcd.putstr(str(latDDWP)+str(latMMmmmmWP)+"N"+str(lonDDWP)+str(lonMMmmmmWP)+lonEWWP)
    if lonEWWP == "W":
        lonDDWP = -lonDDWP
        lonMMmmmmWP = -lonMMmmmmWP

# self-defined function for calculation of true course and distance to waypoint
def pos2WP():
    global latDD, latMMmmmm, lonDD, lonMMmmmm, lonEW, latDDWP, latMMmmmmWP, lonDDWP, lonMMmmmmWP, lonEWWP, tCourse, distance
    if lonEW == "E":
        intlonDD = int(lonDD)
        floatlonMMmmmm = float(lonMMmmmm)
    elif lonEW == "W":
        intlonDD = - int(lonDD)
        floatlonMMmmmm = - float(lonMMmmmm)
    deltaPhi = 60*(latDDWP - int(latDD)) + (latMMmmmmWP - float(latMMmmmm));
    deltaY = deltaPhi * 1.852;
    deltaLambda = 60*(lonDDWP - intlonDD) + (lonMMmmmmWP - floatlonMMmmmm);
    deltaX = deltaLambda * 1.852 * cos(radians((latDDWP+int(latDD))/2));
    if (abs(deltaY)<0.5):
        if (deltaX < 0.1 and deltaX > -0.1):
            tCourse = 1359
            distance = 0
        elif (deltaX > 0): 
            tCourse = 90;
            distance = deltaX
        elif (deltaX < 0): 
            tCourse = 270
            distance = - deltaX

    elif (deltaY>0): 
        if (deltaX < 0.1 and deltaX > -0.1):
            tCourse = 360;
            distance = deltaY
        elif (deltaX > 0):
            tCourse = (90 - degrees(atan2(deltaY,deltaX)))
            distance = sqrt((deltaX*deltaX) + (deltaY*deltaY))
        elif (deltaX < 0): 
            tCourse = (90 - degrees(atan2(deltaY,deltaX)))
            distance = sqrt((deltaX*deltaX) + (deltaY*deltaY))

    elif (deltaY<0):  
        if (deltaX < 0.1 and deltaX > -0.1): 
            tCourse = 180;
            distance = -deltaY
        elif (deltaX > 0): 
            tCourse = 90 - degrees(atan2(deltaY,deltaX))
            distance = sqrt((deltaX*deltaX) + (deltaY*deltaY))
        elif (deltaX < 0): 
            tCourse = 90 - degrees(atan2(deltaY,deltaX))
            distance = sqrt((deltaX*deltaX) + (deltaY*deltaY))
      
    if (tCourse < 0):
        tCourse = tCourse+360
    if (tCourse > 360):
        tCourse = tCourse-360      
    print("tCourse = ",int(tCourse))
    print("Distanz ", distance)
    print()  # blank line

while True:
    try:
        while gps_serial.any():
            data = gps_serial.read()
            for byte in data:
                stat = gps.update(chr(byte))
                if stat is not None:
                    # Print parsed GPS data
                    timeUTC = gps.timestamp
                    print('UTC:  ' + timeString(timeUTC))                
                    dateShort = gps.date_string('short')
                    print('Date:', dateString(dateShort))
                    latitude = gps.latitude_string()
                    latString(latitude)
                    print('Latitude: ', latPrint)                
                    longitude = gps.longitude_string()
                    lonString(longitude)
                    print('Longitude:', lonPrint)
                    print('Altitude:', gps.altitude)
                    print('Satellites in use:', gps.satellites_in_use)
    #                print('Satellites used:', gps.satellites_used)                
    #                print('Horizontal Dilution of Precision:', gps.hdop)
                    print("Waypoint: ",latDDWP,"°",latMMmmmmWP,"'N",lonDDWP,"°",lonMMmmmmWP,"'",lonEWWP)
                    lcd.move_to(0, 0)
                    lcd.putstr(dateString(dateShort) + "  "+ timeString(timeUTC))
                    lcd.move_to(0, 1)
                    lcd.putstr(latLCD+lonLCD)
    #                lcd.move_to(0, 2)
    #                lcd.putstr(str(latDDWP)+str(latMMmmmmWP)+"N"+str(lonDDWP)+str(lonMMmmmmWP)+lonEWWP)                
                    pos2WP()
                    lcd.move_to(0, 3)
                    tCourse
                    lcd.putstr("C: "+str(int(tCourse)) + " D: " + str(round(distance,3))) 
                     
            key_pressed = keypad.read_keypad()
            if key_pressed == '*':
                enterWP()
            sleep(1)

    except:
        sleep(5)            
        pass