'''
This script deals with attempting to send data.
'''

import serial
import numpy as np
import time

import struct

def convert_16bit_to_bytes_struct(data_16bit):
    """
    Packs a list of 16-bit unsigned integers into a bytes object using big-endian format.
    Each 16-bit int becomes 2 bytes (LSB first).
    """
    return struct.pack('>' + 'H' * len(data_16bit), *data_16bit)



# function to fill buffer
def fillBuffer(val):
    buffer = [i & 0xFFFF for i in range(val, val + 512)]

    #print(buffer[:10])
    return convert_16bit_to_bytes_struct(buffer)

def generate_uint8_sine_wave(samples_per_period=3072):
    """
    Generates one period of a sine wave as uint8 values (0–255) with the given number of samples.
    Returns a NumPy array of dtype=np.uint8.
    """
    t = np.linspace(0, 2 * np.pi, samples_per_period, endpoint=False)
    sine_wave = np.sin(t)

    # Scale to [0, 255] and convert to uint8
    sine_uint8 = ((sine_wave + 1.0) * 127.5).astype(np.uint8)

    return sine_uint8


def generate_uint8_square_wave(samples=3072, high=255, low=0, interval=1):
    """
    Generate a square wave with 'interval' samples high, then 'interval' samples low,
    repeated to fill 'samples' total. Output is a NumPy uint8 array.
    """
    buffer = np.zeros(samples, dtype=np.uint8)

    for i in range(0, samples):
        if (i // interval) % 2 == 0:
            buffer[i] = high & 0xFF
        else:
            buffer[i] = low & 0xFF

    return buffer


# Set sample rate
SAMPLE_RATE = 44100
SAMPLE_PERIOD = 1 / SAMPLE_RATE

# Setup communication
BAUD_RATE = 921600
ser = serial.Serial(
    port='COM6',          # Change this to your actual port (e.g., /dev/ttyUSB0)
    baudrate=BAUD_RATE,        # Baud rate
    bytesize=8,           # 8 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bits
    timeout=None,             # Timeout in seconds
    write_timeout=None
)

if ser is None:
    raise ValueError('Com failed')

# Reset buffer
ser.reset_input_buffer()
print("Sending stereo audio...")

value = 0


sin_buf = bytes(generate_uint8_sine_wave())

square_buf = bytes(generate_uint8_square_wave())



try:
    while True: 
        input(f'Enter to send {value} - {value + 512}')
        #ser.write(square_buf)

        for i in range(5):
            
            buff = fillBuffer(value)
            print(f"Sending {buff[:10]}")
            value += 512
            ser.write(buff)
            input()
           

except KeyboardInterrupt:
    print(f'Sent {value} data points')

finally:
    ser.reset_input_buffer()
    ser.close()
