# Raspberry Pi Pico and GPS-module SIM808
# Get GPS position and send SMS with AT commands
# 


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
# preparations:
GNRMC = "110208.000,A,5354.6764,N,00952.2245,E,0.833,3.73,191224"  # test position, place holder
print(sendATCmd("AT"))
print(sendATCmd("AT+CGPSPWR=1"))
time.sleep(5)
print(sendATCmd("AT+COPS?"))	# Display the current network operator 


while (True):
    dataString = sendATCmd("AT+CGPSINF=32")
    print("dataString=",dataString)
    dataList = dataString.split(",")
#    print("dataList=",dataList)
    if dataList[2] == "A":
        print("Signal okay")
#        GNRMC = dataList[1]+" "+dataList[3]+dataList[4]+" "+dataList[5]+dataList[6]
        GNRMC = dataString
        print("GNRMC = ", GNRMC)
        print(sendATCmd("AT+CMGF=1\r\n"))	# Select SMS Message Format
        print(sendATCmd("AT+CSCA=\"+491722270333\"\r\n"))   #here: Vodafone, change to your service provider
        print(sendATCmd("AT+CMGS=\"+491782353013\"\r\n"))	# own tel.number, receiver of SMS
        sendATCmd(GNRMC+"\x1a\r\n"+"\x1b\r\n")		# SMS text (here vaiable GNRMC), then Ctrl-Z an ESC
        time.sleep(300)
    time.sleep(3)
    