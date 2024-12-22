# Raspberry Pi Pico and GPS ublox NEO-6M or NEO-7M
# receive data via UART1 (Tx=GP4, RX=GP5)
# based on Module micropyGPS by Michael Calvin McCoy
# download and save in sub-directory /lib
# https://github.com/inmcm/micropyGPS/blob/master/micropyGPS.py

from machine import UART, Pin
from time import sleep
from micropyGPS import MicropyGPS

# Instantiate the micropyGPS object
gps = MicropyGPS()

# Instantiate the UART object 
gps_serial = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

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

while True:
    while gps_serial.any():
        data = gps_serial.read()
        for byte in data:
            stat = gps.update(chr(byte))
            if stat is not None:
                # Print parsed GPS data
                timeUTC = gps.timestamp
                dateShort = gps.date_string('short')
                print('UTC:  ' + timeString(timeUTC))
                print('Date:', dateString(dateShort))
                print('Latitude:', gps.latitude_string())
                print('Longitude:', gps.longitude_string())
                print('Altitude:', gps.altitude)
                print('Satellites in use:', gps.satellites_in_use)
#                print('Satellites used:', gps.satellites_used)                
#                print('Horizontal Dilution of Precision:', gps.hdop)
                print()
        sleep(1)

