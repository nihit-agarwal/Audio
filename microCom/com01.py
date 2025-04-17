'''
This file is about establishing SCI communication with C2000, F28379D launchpad
Script receives 8 bit uint at 9600, 1000000 baud and prints it out to terminal
It messes up when receiving data too fast.
Look into adc lab with SCI added in CCS for other details.

'''

import serial
import struct
import time

# print out com ports
import serial.tools.list_ports
ports  = serial.tools.list_ports.comports()
for port in ports:
    print(port.device) 

# Setup communication
BAUD_RATE = 3125000
ser = serial.Serial(
    port='COM3',          # Change this to your actual port (e.g., /dev/ttyUSB0)
    baudrate=BAUD_RATE,        # Baud rate
    bytesize=8,           # 8 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bits
    timeout=0             # Timeout in seconds
)

if ser is None:
    raise ValueError('Com failed')

# Reset buffer
ser.reset_input_buffer()

# Set constants for communication
running = True
sample_size = 180
print("Receiving stereo audio...")

data = []
count = 0
raw_data = []
received = []
try:
    while count < 24000: # and shared_queue.empty():

        if ser.in_waiting >= sample_size:
            #start = time.perf_counter()
            raw_data = ser.read(sample_size)
            data.extend(raw_data)
            count += 60
            #stop = time.perf_counter()
            #if stop - start > (30 * 0.000022):
            #    print('Error')
            #values = [hex(i) for i in raw_data]
            #print(values)

          

            
        else:
            pass 
    #print(value)
except KeyboardInterrupt:
    print(f'Received {count} data points')
    
finally:
    ser.close()
    #data = [hex(i) for i in data]
    # Check for error
    
    for i in range(0, len(data), 3):
        value = (data[i + 2] << 8) + data[i + 1]
        received.append(value)
        if data[i] != 0xaa:
            print(data[i])
            print('Error')
            break
    print(data[:18])
    print(len(received))
    print(received[:100])
    
            
    
    

    




