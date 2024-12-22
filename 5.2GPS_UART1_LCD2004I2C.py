# Raspberry Pi Pico and GPS ublox NEO-6M or NEO-7M
# receive data via UART1 (Tx=GP4, RX=GP5)
# based on Module micropyGPS by Michael Calvin McCoy
# download and save in sub-directory /lib
# https://github.com/inmcm/micropyGPS/blob/master/micropyGPS.py

from machine import UART, I2C, Pin
from time import sleep
from micropyGPS import MicropyGPS
from machine_i2c_lcd import I2cLcd

# Instantiate the micropyGPS object
gps = MicropyGPS()

# Instantiate the UART object 
gps_serial = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

# Instantiate LCD2004 with I2C-Adapter
# The PCF8574 has a jumper selectable address: 0x20 - 0x27
DEFAULT_I2C_ADDR = 0x27
# On the RPi Pico, I2C0 shows up on GP0 (sda) and GP1 (scl)
i2c = I2C(0, sda=0, scl=1, freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 4, 20)

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
    latList = latitude.split("°")
    latDD = latList[0]
    latList2 = latList[1].split("'")
    latMM = latList2[0]
    latNS = latList2[1]
    return latDD.strip()+"°"+ latMM.strip()+"'"+ latNS.strip()
    
# self-defined function for better presentation of the longitude
def lonString(longitude):
    lonList = longitude.split("°")
    lonDDD = lonList[0]
    if int(lonDDD) < 100:
        lonDDD = "0"+lonDDD
    if int(lonDDD) < 10:
        lonDDD = "0"+lonDDD                    
    lonList2 = lonList[1].split("'")
    lonMM = lonList2[0]
    lonEW = lonList2[1]
    return lonDDD.strip()+"°"+ lonMM.strip()+"'"+ lonEW.strip()
    

while True:
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
                print('Latitude: ', latString(latitude))
                longitude = gps.longitude_string()
                print('Longitude:', lonString(longitude))
                print('Altitude:', gps.altitude)
                print('Satellites in use:', gps.satellites_in_use)
#                print('Satellites used:', gps.satellites_used)                
#                print('Horizontal Dilution of Precision:', gps.hdop)
                print()  # blank line
                lcd.move_to(0, 0)
                lcd.putstr('UTC:  ' + timeString(timeUTC))
                lcd.move_to(0, 1)
                lcd.putstr('Date: ' + dateString(dateShort))
                lcd.move_to(0, 2)
                lcd.putstr('Lat: ' + latString(latitude).replace("°","\xDF"))
                lcd.move_to(0, 3)
                lcd.putstr('Lon: ' + lonString(longitude).replace("°","\xDF"))
        sleep(1)

