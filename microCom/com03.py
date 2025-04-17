"""
Attempt receiving data using alignment
"""

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
#sample_size = 2
print("Receiving stereo audio...")

data = []
count = 0
try:
    while running: # and shared_queue.empty():
        if ser.in_waiting > 0:
            header = ser.read(1)
            if header == b'\xAA':
                raw_data = ser.read(2)

                value = int.from_bytes(raw_data, byteorder='little')
                print(f" Hex : {hex(value)} and value: {value}")
                count += 1
            else:
                print(f"Received wrong: ", header)
                pass 
    print(value)
except KeyboardInterrupt:
    print(f'Received {count} data points')
    ser.reset_input_buffer()
    ser.close()
    