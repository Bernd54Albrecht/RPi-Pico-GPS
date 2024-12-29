# Raspberry Pi Pico and GPS-module SIM808
# Get GPS position and send SMS at given interval(line 11)
# Insert SMS recipient in line 15
# Micro-Python module SIM800 required
# https://github.com/Bernd54Albrecht/RPi-Pico-GPS

from SIM800 import GPS
import time
import sys

gps = GPS(0)
interval = 10	# send SMS at given interval in minutes

while True:
    try:
        gps.check_start()
        gps.sendPosition('"+49123456789"')   # insert SMS recipient as String
        time.sleep(10)
        gps.power_on_off()
        time.sleep(60*interval)
        
    except KeyboardInterrupt:
        sys.exit()
        
    except RuntimeError:
        pass