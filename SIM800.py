# Self-defined MicroPython Module for
# Raspberry Pi Pico and GPS-module SIM808/868
# Get GPS position
# Receive and send SMS with AT commands
# https://github.com/Bernd54Albrecht/RPi-Pico-GPS

# Import MicroPython Modules (libraries)
from machine import UART, Pin
import time

pwr_en = Pin(14, Pin.OUT)
led_onboard = Pin("LED",Pin.OUT)

class GPS:
    
    # Initialisation of UART(RX/TX)
    # UART 0, tx=GP0 (phys. Pin 1), rx=GP1 (phys. Pin 2)
    # UART 1, tx=GP4 (phys. Pin 6), rx=GP5 (phys. Pin 7)
    def __init__(self,uart=0):
        self.serial = UART(uart, baudrate=9600)


    # Switch on/off the GPS receiver with Pin GP14
    def power_on_off(self):
        pwr_key = Pin(pwr_en, Pin.OUT)
        pwr_key.value(1)
        time.sleep(2)
        pwr_key.value(0)
        time.sleep(2)

    # self-defined function to send AT-Command and receive feedback
    def sendATCmd (self,at_cmd):
        char = ''
        dataString = ''
        self.serial.write(at_cmd + '\r\n')
        time.sleep(2)
        while (char is not None):
            char = self.serial.read(1)
            try:
                dataString += char.decode('utf-8')
            except: pass
        if at_cmd + '\r\n' == dataString: return 're-check connections'
        return dataString

    # function for LED_BUILTIN
    def led_builtin(self, onoff):
        if onoff == 1:
            led_onboard.value(1)
        else:
            led_onboard.value(0)

    # Module startup detection
    def check_start(self):
        if 'OK' in self.sendATCmd("AT"):
            print('SIM868 is ready\r\n')
            self.sendATCmd("AT+CGPSPWR=1")
            return
        else:        
            print('SIM868 is starting up, please wait...\r\n')
            self.power_on_off()
            self.check_start()

    def sendPosition(self,toAddressee):
        dataString = self.sendATCmd("AT+CGPSINF=32")
        print("dataString=",dataString)
        dataList = dataString.split(",")
    #    print("dataList=",dataList)
        if dataList[2] == "A":
            print("Signal okay")
# options for SMS message format:            
#            GNRMC = dataString            
#            GNRMC = dataList[1]+" "+dataList[3]+dataList[4]+" "+dataList[5]+dataList[6]
# best format for Google Maps:
            BBMMmmmm = float(dataList[3])
            BB = int(BBMMmmmm/100)
            print("BB = ",BB)
            BMmmmm = BBMMmmmm - 100*BB
            print("BMmmmm = ",BMmmmm)
            LLMMmmmm = float(dataList[5])
            LL = int(LLMMmmmm/100)
            print("LL = ",LL)
            LMmmmm = LLMMmmmm - 100*LL
            print("LMmmmm = ",LMmmmm)            
            GNRMC = str(BB) + " " + str(BMmmmm) +" "+ dataList[4] +" "+ str(LL) +" "+ str(LMmmmm) +" "+ dataList[6]
            print("GNRMC = ", GNRMC)
            print(self.sendATCmd("AT+CMGF=1\r\n"))	# Select SMS Message Format
            print(self.sendATCmd("AT+CSCA=\"+491722270333\"\r\n"))   #here: Vodafone, change to your service provider
# 			send position to sending mobile phone
            print(self.sendATCmd("AT+CMGS="+toAddressee+"\r\n"))	# requesting phone number = receiver of SMS
# 			send position to own mobile phone
#            print(self.sendATCmd("AT+CMGS=\"+49123456789\"\r\n"))	# own tel.number, receiver of SMS
            self.sendATCmd(GNRMC+"\x1a\r\n"+"\x1b\r\n")		# SMS text (here vaiable GNRMC), then Ctrl-Z an ESC
        else: self.sendPosition(toAddressee)
        
    def receiveSMS(self):
        self.sendATCmd("AT+CMGF=1")
        SMSstring = self.sendATCmd('AT+CMGL="ALL",0')
        print("SMSstring = ",SMSstring)
        self.sendATCmd("AT+CMGD=12,2")
        return SMSstring
        
        