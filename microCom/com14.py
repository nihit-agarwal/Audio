"""
Very basic send script
"""

import serial
# Setup communication
BAUD_RATE = 9600
ser = serial.Serial(
    port='COM3',          # Change this to your actual port (e.g., /dev/ttyUSB0)
    baudrate=BAUD_RATE,        # Baud rate
    bytesize=8,           # 8 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bits
    
)

if ser is None:
    raise ValueError('Com failed')


c = 0
while True:
    c &= 0xFF
    input(f'Hit Enter to send {c}')
    ser.write(bytes(c))
    c += 1
    
    
    