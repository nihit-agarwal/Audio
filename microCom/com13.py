'''
This script deals with trying to send 8-bit/16-bit gagnam style.
'''

import serial
import numpy as np
import time
from scipy.io import wavfile
import struct

import psutil
import os

def set_process_priority():
    # Set process priority
    process = psutil.Process(os.getpid())
    try:
        process.nice(psutil.HIGH_PRIORITY_CLASS)
        print("Process priority set to HIGH")
    except:
        print("Failed to set process priority, may need admin rights")

set_process_priority()

USE_8_BIT = False

NUM_SAMPLES = 512 

def convert_16bit_to_bytes_struct(data_16bit):
    """
    Packs a list of 16-bit unsigned integers into a bytes object using big-endian format.
    Each 16-bit int becomes 2 bytes (LSB first).
    """
    return struct.pack('>' + 'H' * len(data_16bit), *data_16bit)


def read_wav_as_uint16_chunks(filename='gagnam.wav', chunk_size=NUM_SAMPLES):
    """
    Reads a WAV file, converts it to uint16, and returns a list of lists,
    each containing `chunk_size` samples.
    """
    sample_rate, data = wavfile.read(filename)

    # If stereo, take only one channel (left)
    if data.ndim > 1:
        data = data[:, 0]

    if data.dtype != np.int16:
        raise ValueError("Expected 16-bit PCM WAV file")

    # Convert int16 [-32768, 32767] to uint16 [0, 65535]
    data_uint16 = (data.astype(np.int32) + 32768).astype(np.uint16)
    print(np.min(data_uint16), np.max(data_uint16))

    # Chunk into list of lists
    chunks = [
        convert_16bit_to_bytes_struct(data_uint16[i:i + chunk_size].tolist())
        for i in range(0, len(data_uint16), chunk_size)
        if len(data_uint16[i:i + chunk_size]) == chunk_size
    ]

    return chunks

def read_wav_and_chunk_to_uint8(filename='gagnam.wav', chunk_size=NUM_SAMPLES * 2):
    # Step 1: Load WAV file
    rate, data = wavfile.read(filename)
    print(f"Loaded WAV: {filename}, Sample rate: {rate}, Samples: {len(data)}")

    # Step 2: Take only one channel if stereo
    if data.ndim > 1:
        data = data[:, 0]

    # Step 3: Convert to uint8
    if data.dtype == np.int16:
        # Scale from [-32768, 32767] to [0, 255]
        data = ((data.astype(np.float32) / 32768.0 + 1.0) * 127.5).astype(np.uint8)
    else:
        raise ValueError("Expected 16-bit PCM WAV (int16 format)")

    # Step 4: Split into chunks
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        if len(chunk) == chunk_size:
            chunk = bytes(chunk.tolist())
            chunks.append(chunk)
    print(f"Generated {len(chunks)} chunks of {chunk_size} samples each.")
    return chunks



# Static gloabal variables
if USE_8_BIT:
    chunks = read_wav_and_chunk_to_uint8()
    BAUD_RATE = 441000
else:
    chunks = read_wav_as_uint16_chunks()
    BAUD_RATE = 921600
chunk_id = 0


def get_chunk(chunk_no=None):
    global chunk_id
    if chunk_no == None:
        i = chunk_id
        chunk_id += 1
    else:
        i = chunk_no
    
    return chunks[i]

#BAUD_RATE = 882000
# Set sample rate
SAMPLE_RATE = 44100
SAMPLE_PERIOD = 1 / SAMPLE_RATE

# Setup communication
          
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

try:
    while True: 
        music_buf = get_chunk()
        t = time.perf_counter()
        #print(f"# Sending at {t:6f}")
        ser.write(music_buf)
        print(f"Completed in {(time.perf_counter() - t)}")
           

except KeyboardInterrupt:
    #print(f'Sent {value} data points')
    pass

finally:
    ser.reset_input_buffer()
    ser.close()
