from machine import Pin
from keypad import Keypad
from time import sleep

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

while True:
    key_pressed = keypad.read_keypad()
    if key_pressed:
        print("Key pressed:", key_pressed)
    sleep(0.2)  # debounce and delay