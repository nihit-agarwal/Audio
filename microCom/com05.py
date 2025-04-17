'''
This script deals with attempting to send data.
'''

import serial
import numpy as np
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
print("Sending stereo audio...")

value = 0
try:
    while value < 50000: 
        sendChar = np.uint8(value & 0xFF).tobytes()
        ser.write(sendChar)
        value += 1
          
        
   
except KeyboardInterrupt:
    print(f'Sent {value} data points')

finally:
    ser.reset_input_buffer()
    ser.close()
