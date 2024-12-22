# Raspberry Pi Pico and GPS-module SIM808
# initial trials with AT commands
# Enter AT and get OK
# Enter AT+CGPSPWR=1 and get OK 
# Enter repeatedly AT+CGPSINF=32 and get GPS data
# command for repition also A/

# Import MicroPython Modules (libraries)
from machine import UART, Pin
import time

# Initialisation of UART(RX/TX)
# UART 0, TX=GP0 (phys. Pin 1), RX=GP1 (phys. Pin 2)
# UART 1, TX=GP4 (phys. Pin 6), RX=GP5 (phys. Pin 7)
gps_serial = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

# Switch on GPS receiver with Pin D9
d9 = Pin(9, Pin.OUT)
d9.on()
time.sleep(1)
d9.off()


# self-defined function to send AT-Command and receive feedback
def sendATCmd (at_cmd):
    char = ''
    dataString = ''
    gps_serial.write(at_cmd + '\r\n')
    time.sleep(2)
    while (char is not None):
        char = gps_serial.read(1)
        try:
            dataString += char.decode('utf-8')
        except: pass
    if at_cmd + '\r\n' == dataString: return 're-check connections'
    
    return dataString

# Main loop
# Enter AT-Commands
while (True):
    at_cmd = input('AT-Command: ')
    print(sendATCmd(at_cmd))