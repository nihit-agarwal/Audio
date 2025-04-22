"""
This file handles:
1. Read
2. Send
3. Compute
"""

# Imports
import serial
import time
import threading
from queue import Queue
from helpers import *
from numpy import np

# Setup serial comm
BAUD_RATE = 882000
NUM_SAMPLES = 512
PORT = 'COM6'
ser = None


# Queue stuff
procQ = None
sendQ = None

# Music stuff
chunks = None
chunk_id = None

# ML stuff
LABEL = "glass_breaking"
soundIsolate = None

import psutil
import os

def generate_frequency_sweep_chunks(duration=30, start_freq=20, end_freq=20000,
                                     sample_rate=44100, chunk_size=512):
    """
    Generates a logarithmic frequency sweep and returns audio in chunks.

    Parameters:
    - duration (float): Duration of the sweep in seconds.
    - start_freq (float): Starting frequency in Hz.
    - end_freq (float): Ending frequency in Hz.
    - sample_rate (int): Sampling rate in Hz.
    - chunk_size (int): Number of samples per buffer.

    Returns:
    - List[np.ndarray]: List of audio chunks (16-bit PCM samples).
    """
    # Time vector
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Logarithmic frequency sweep
    sweep = np.sin(2 * np.pi * start_freq * ((end_freq / start_freq) ** (t / duration) - 1) / np.log(end_freq / start_freq))
    
    # Normalize to 16-bit PCM range
    sweep_int16 = np.int16(sweep / np.max(np.abs(sweep)) * 32767)

    # Split into chunks
    chunks = [sweep_int16[i:i+chunk_size] for i in range(0, len(sweep_int16), chunk_size)]
    
    return chunks

def set_process_priority():
    # Set process priority
    process = psutil.Process(os.getpid())
    try:
        process.nice(psutil.HIGH_PRIORITY_CLASS)
        print("Process priority set to HIGH")
    except:
        print("Failed to set process priority, may need admin rights")

set_process_priority()

def audio_inject(musicBuf, inputBuf):
    """
    Method to take in uint16 music and add the ML data to it
    Returns list of uint16 samples
    @param[in] musicBuf uint16 samples of musics
    @param[in] inputBuf uint16 audio input samples
    """
    global soundIsolate

    ouput_audio_chunk = soundIsolate.run(LABEL, inputBuf)
    # Need to edit

    return musicBuf

# Thread to send data to DMA
def receive_fn():
    global procQ, ser
    while True:
        recBuf = ser.read(NUM_SAMPLES * 2)
        procQ.put(recBuf)

# Thread to receive data from DMA
def send_fn():
    global sendQ, ser
    while True:
        outBuf = sendQ.get()
        ser.write(outBuf)

# Thread to compute music / ML
def compute_fn():
    global procQ, sendQ, chunks, chunk_id
    firstComputed = False
    while True:
        outBuf = chunks[chunk_id]
        chunk_id += 1
        chunk_id = chunk_id % len(chunks)
        if not firstComputed:
            if not procQ.empty():
                inputAud = procQ.get()
                inputAud = convert_bytes_to_16bit_list(inputAud, NUM_SAMPLES)
                outBuf = audio_inject(outBuf, inputAud)
                firstComputed = True
        else:
            inputAud = procQ.get()
            inputAud = convert_bytes_to_16bit_list(inputAud, NUM_SAMPLES)
            outBuf = audio_inject(outBuf, inputAud)

        # Convert uint16 to bytes
        outBuf = convert_16bit_to_bytes_struct(outBuf)
        sendQ.put(outBuf)
        



def main():
    global sendQ, procQ, chunks, chunk_id, ser, soundIsolate
    # Thread safe global queues
    sendQ = Queue(maxsize=1)
    procQ = Queue(maxsize=1)

    # Music play stuff
    # chunks = read_wav_as_uint16_chunks(chunk_size=NUM_SAMPLES)
    chunks = generate_frequency_sweep_chunks()
    chunk_id = 0

    # Initialize the model to use for processing
    soundIsolate = audioML.AudioExtractor()
    soundIsolate.initialize_model()
    

    # Serial comm setup
    ser = serial.Serial(
    port=PORT,          # Change this to your actual port (e.g., /dev/ttyUSB0)
    baudrate=BAUD_RATE,        # Baud rate
    bytesize=8,           # 8 data bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE,  # 1 stop bits
    timeout=None,             # Timeout in seconds  
    )

    if ser is None:
        raise ValueError('Com failed')

    # Create threads
    print('Starting threads')
    receiveThread = threading.Thread(target=receive_fn)
    sendThread = threading.Thread(target=send_fn)
    computeThread = threading.Thread(target=compute_fn)

    try:
        # Start threads
        receiveThread.start()
        sendThread.start()
        computeThread.start()

        # Busy wait
        while True:
            pass
    except KeyboardInterrupt:
        print('Ending threads')
    


if __name__ == '__main__':
    main()


    
