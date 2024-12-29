# MicroPython program
# Raspberry Pi Pico and GPS-module SIM808/868
# Get GPS position
# Receive and send SMS with AT commands
# https://github.com/Bernd54Albrecht/RPi-Pico-GPS

from SIM800 import GPS
import time

gps = GPS()	# self-defined module with functions

while True:
    try:
        gps.check_start()
        SMSstring = gps.receiveSMS()
        SMSlist = SMSstring.split(",")
        lenSMSlist = len(SMSlist)
        if lenSMSlist>2: 
            print("len(SMSlist)",lenSMSlist)
            toAddressee = SMSlist[3]
            print(toAddressee)
            text = SMSlist[6].split('"')[1]
            print("text: ", text)
            if "SMS" in text.upper():
                gps.sendPosition(toAddressee)
            
        time.sleep(30)
        
    except KeyboardInterrupt:
        sys.exit()
        
    except RuntimeError:
        pass    

