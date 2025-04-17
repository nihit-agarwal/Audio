'''
This script deals with attempting to send data.
'''

import serial
import csv
import numpy as np
import soundfile as sf
import time

# Set sample rate
SAMPLE_RATE = 44100
T_PERIOD = 1 / SAMPLE_RATE

# Setup communication
BAUD_RATE = 3125000
ser = serial.Serial(
    port='COM3',          # Change this to your actual port (e.g., /dev/ttyUSB0)
    baudrate=BAUD_RATE,        # Baud rate
    bytesize=8,           # 8 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bits
    timeout=5,             # Timeout in seconds
    write_timeout=0.1
)

if ser is None:
    raise ValueError('Com failed')

# Reset buffer
ser.reset_input_buffer()

# Set constants for communication
running = True
#sample_size = 2
print("Receiving stereo audio...")

#data = []
count = 0
value = 300
start = time.perf_counter()
try:
    while value < 50000: # and shared_queue.empty():
        stop = time.perf_counter()
        if stop - start >= T_PERIOD:
            start = stop
            #value  = ser.read(1)
            #value = int.from_bytes(value, byteorder='big')
            value += 1
            #value &= 0xFF
            sendVal = np.uint8(value & 0xFF)
            print('Send val is ', sendVal.tobytes())
            ser.write(sendVal.tobytes())
            
            sendVal2 = np.uint8((value >> 8) & 0xFF)
            ser.write(sendVal2.tobytes())
            print('Send val is ', sendVal2.tobytes())
            print(f" Hex : {hex(value)} and value: {value}, value written : {sendVal} and {sendVal2}")
            input()
            
            #input()

        
    print(value)
except KeyboardInterrupt:
    print(f'Received {count} data points')
    ser.reset_input_buffer()
    ser.close()
