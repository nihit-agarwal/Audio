'''
This file is about reading data in batches. Starting with uint8.

'''

import serial
import struct
import time


USE_8BIT = False
SAMPLE_SIZE = 1024
value = 0


# Setup communication
if USE_8BIT:
    BAUD_RATE = 441000
else:
    BAUD_RATE = 882000

ser = serial.Serial(
    port='COM6',          # Change this to your actual port (e.g., /dev/ttyUSB0)
    baudrate=BAUD_RATE,        # Baud rate
    bytesize=8,           # 8 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bits
    timeout=None             # Timeout in seconds
)

def check_integrity(buf):
    global value
    if USE_8BIT:
        buf = list(buf)
        for i in range(len(buf)):
            if buf[i] != value:
                pass  
            value += 1
            value &= 0xFF
    else:
        buf = list(struct.unpack(f'>{SAMPLE_SIZE//2}H', buf))
        for i in range(0, len(buf)):
            if buf[i] != value:
                pass
            value += 1
            value &= 0xFFFF


        


# Reset buffer
ser.reset_input_buffer()

# Set constants for communication

try:
    buf = ser.read(SAMPLE_SIZE)
    check_integrity(buf)
    pass
    # while True:
    #     buf = ser.read(SAMPLE_SIZE)
    #     check_integrity(buf)
except KeyboardInterrupt:
    print(f'Stopped reading')
    
finally:
    ser.close()

    
            
    
    

    




