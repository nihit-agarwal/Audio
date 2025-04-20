"""
This file contains helper functions
"""

from scipy.io import wavfile
import struct
import numpy as np
from isolation import audioML

def convert_bytes_to_16bit_list(bytes_data, num_samples=512):
    """
    Unpacks the bytes data to uint16 numbers
    """
    return list(struct.unpack(f'>{num_samples}H', bytes_data))

def convert_16bit_to_bytes_struct(data_16bit):
    """
    Packs a list of 16-bit unsigned integers into a bytes object using big-endian format.
    Each 16-bit int becomes 2 bytes (LSB first).
    """
    return struct.pack('>' + 'H' * len(data_16bit), *data_16bit)


def read_wav_as_uint16_chunks(filename='microCom/gagnam.wav', chunk_size=512):
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

    # Chunk into list of lists
    chunks = [
        data_uint16[i:i + chunk_size].tolist()
        for i in range(0, len(data_uint16), chunk_size)
        if len(data_uint16[i:i + chunk_size]) == chunk_size
    ]

    return chunks

