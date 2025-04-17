'''
This script deals with attempting to send data.
'''

import serial
import numpy as np
import time


# function to fill buffer
def fillBuffer(val):
    buffer = [i & 0xFF for i in range(val, val + 3072)]
    print(buffer[:10])
    return buffer
# Set sample rate
SAMPLE_RATE = 44100
SAMPLE_PERIOD = 1 / SAMPLE_RATE

# Setup communication
BAUD_RATE = 441000
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
print("Sending stereo audio...")

value = 0
try:
    while True: 
        input(f'Enter to send {value} - {value + 5}')
        
        for i in range(5):
            curr_time = time.perf_counter()
            buff = bytes(fillBuffer(value))
            print(f"Sending {buff[:10]}")
            value += 3072
            ser.write(buff)
           


        
        
          
        
   
except KeyboardInterrupt:
    print(f'Sent {value} data points')

finally:
    ser.reset_input_buffer()
    ser.close()
