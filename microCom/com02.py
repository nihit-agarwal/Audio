'''
This file is about establishing SCI communication with C2000, F28379D launchpad
Script receives 16 bit uint at 9600 baud and prints it out to terminal
It messes up when receiving data too fast.
Look into adc lab with SCI added in CCS for other details.

'''

import serial


# Setup communication
BAUD_RATE = 3125000
ser = serial.Serial(
    port='COM3',          # Change this to your actual port (e.g., /dev/ttyUSB0)
    baudrate=BAUD_RATE,        # Baud rate
    bytesize=8,           # 8 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bits
    timeout=5             # Timeout in seconds
)

if ser is None:
    raise ValueError('Com failed')

# Reset buffer
ser.reset_input_buffer()

# Set constants for communication
running = True
sample_size = 2
print("Receiving stereo audio...")

data = []
count = 0
try:
    while running: # and shared_queue.empty():
        if ser.in_waiting >= sample_size:
            raw_data = ser.read(sample_size)

            value = int.from_bytes(raw_data, byteorder='big') 
            #value = ((value & 0xFF) << 8) + (value >> 8)
            print(f" Hex : {hex(value)} and value: {value}")
            count += 1
            
        else:
            pass 
    print(value)
except KeyboardInterrupt:
    print(f'Received {count} data points')
    ser.close()
    




