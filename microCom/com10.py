"""
Testing agenda:
1. Retrieve data from buffer when size reaches 2048 bytes
2. Process data into uint format of 1024 samples
"""


import serial
import struct

# Setup communication
BAUD_RATE = 3125000
ser = serial.Serial(
    port='COM3',          # Change this to your actual port (e.g., /dev/ttyUSB0)
    baudrate=BAUD_RATE,        # Baud rate
    bytesize=8,           # 8 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bits
    timeout=0            # Timeout in seconds
)

if ser is None:
    raise ValueError('Com failed')

# Reset buffer
ser.reset_input_buffer()

# Set constants for communication
running = True
ingestion_size = 1024 # 1024 samples
print("Receiving stereo audio...")

data = []
numBatches = 0


def convertToSamples(raw_data):
    #samples = [None] * (len(raw_data) // 2)
    
    #for i in range(0,  len(raw_data), 2):
    #    samples[i // 2] = (raw_data[i + 1] << 8) + raw_data[i]
    samples = list(struct.unpack('<512H', raw_data))
    return samples

while numBatches < 5:
    if ser.in_waiting >= ingestion_size:
        raw_data = ser.read(ingestion_size)
        numBatches += 1
        data.extend(convertToSamples(raw_data))
            

         

print(f'Received {numBatches} batches')
ser.reset_input_buffer()
ser.close()
print(data[:1000])
    