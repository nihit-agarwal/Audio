"""
Script to receive data in batches and save to wav file when ctrl-C is hit / on timeout
"""

import serial
import numpy as np
import time
from scipy.io import wavfile
import struct
import soundfile as sf

import signal
import sys




NUM_SAMPLES = 512  # Chunk size in bytes
recorded = []
SAMPLE_RATE = 44100

def convert_bytes_to_16bit_list(bytes_data, num_samples=512):
    """
    Unpacks the bytes data to uint16 numbers
    """
    return list(struct.unpack(f'>{num_samples}H', bytes_data))


def decodeData(buf, recorded):
    samples  = convert_bytes_to_16bit_list(buf, NUM_SAMPLES)
    recorded.extend(samples)


BAUD_RATE = 882000

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



print('Recording mic data for 20 sec')
count = 0
try:
    input('Hit enter to start')
    while count < 2000:
        buf = ser.read(NUM_SAMPLES * 2)
        decodeData(buf, recorded)
        count += 1
except KeyboardInterrupt:
    print('End recording')
finally:
    ser.close()
    print(len(recorded))
    data_uint16 = np.array(recorded, dtype=np.uint16)
    data_int16 = (data_uint16.astype(np.int32) - 32768).astype(np.int16)
    sf.write('sounds/micRecorded.wav', data_int16, SAMPLE_RATE)

    

