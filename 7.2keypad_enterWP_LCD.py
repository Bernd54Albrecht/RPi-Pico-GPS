from machine import I2C, Pin
from keypad import Keypad
from time import sleep, sleep_ms, ticks_ms
from machine_i2c_lcd import I2cLcd

# The PCF8574 has a jumper selectable address: 0x20 - 0x27
DEFAULT_I2C_ADDR = 0x27
print("Running LCD test")
# On the RPi Pico, I2C0 shows up on GP0 (sda) and GP1 (scl)
i2c = I2C(0, sda=0, scl=1, freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 4, 20)
lcd.putstr("Press * \nto enter waypoint")
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
NS = "N"
EW = "W"

def keyInput():
    key_pressed = 0
    keyList = []
    for n in range(20):
        keyList.append("1")
    keyString = ""
    i = 0

    while key_pressed!="*":
        key_pressed = keypad.read_keypad()
        if key_pressed:
            print("Key pressed:", key_pressed)
            keyList[i] = key_pressed
            if keyList[i] == 'D':
                i = i - 1
            else:
                i +=1
            print("keyList:", keyList[0:i])
            lcd.clear()
            lcd.move_to(0, 2)
            lcd.putstr(keyList[0:i])            
            if i==20:
                key_pressed = '*'
        sleep(0.2)  # debounce and delay
    sleep(0.5)
    return keyList    

try:
    while True:
        key_pressed = keypad.read_keypad()
        if key_pressed == '*':
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
                EW = "E"
            print(latDDWP,"°",latMMmmmmWP,"'N",lonDDWP,"°",lonMMmmmmWP,"'",EW)
            lcd.clear()
            lcd.move_to(0, 2)            
            lcd.putstr(str(latDDWP)+str(latMMmmmmWP)+"N"+str(lonDDWP)+str(lonMMmmmmWP)+"E")
        sleep(0.1)
except KeyboardInterrupt:
    print("error")
