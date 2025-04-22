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
import csv


# Setup serial comm
BAUD_RATE = 882000
NUM_SAMPLES = 512
PORT = 'COM6'
ser = None

# Closing condition
running = True

# Queue stuff
#procQ = None
sendQ = None

# Music stuff
chunks = None
chunk_id = None

# ML stuff
LABEL = "birds_chirping"
soundIsolate = None

f = open('mloutput.csv', 'a', newline='')
writer = csv.writer(f)

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

def average_uint16_audio(list1, list2):
    # Convert to numpy arrays
    arr1 = np.array(list1, dtype=np.uint16)
    arr2 = np.array(list2, dtype=np.uint16)
    
    # Promote to int32 to avoid overflow, average, then clip
    avg = ((arr1.astype(np.int32) + arr2.astype(np.int32)) // 2)
    
    # Clip to valid uint16 range
    avg = np.clip(avg, 0, 65535).astype(np.uint16)
    
    # Convert back to list if needed
    return avg.tolist()

def audio_inject(musicBuf, inputBuf):
    """
    Method to take in uint16 music and add the ML data to it
    Returns list of uint16 samples
    @param[in] musicBuf uint16 samples of musics
    @param[in] inputBuf uint16 audio input samples
    """
    global soundIsolate

    ouput_audio_chunk, play = soundIsolate.run(LABEL, inputBuf)
    # Need to edit
    # add music
    play = False
    if play:
        mashedBuf = average_uint16_audio(ouput_audio_chunk, musicBuf)
        return mashedBuf
    else:
        return ouput_audio_chunk
    
# Thread to send data to DMA
# def receive_fn():
#     global procQ, ser
#     while True:
#         recBuf = ser.read(NUM_SAMPLES * 2)
#         procQ.put(recBuf)

# Thread to receive data from DMA
def send_fn():
    global sendQ, ser, running
    while running:
        outBuf = sendQ.get()
        ser.write(outBuf)

# Thread to compute music / ML
# def compute_fn():
    # global procQ, sendQ, chunks, chunk_id, running
    # firstComputed = False

    # while running:
    #     outBuf = chunks[chunk_id]
    #     chunk_id += 1
    #     chunk_id = chunk_id % len(chunks)
    #     if not firstComputed:
    #         if ser.in_waiting >= NUM_SAMPLES * 2:
    #             recBuf = ser.read(NUM_SAMPLES * 2)
    #             recBuf = convert_bytes_to_16bit_list(recBuf, NUM_SAMPLES)
    #             outBuf = audio_inject(outBuf, recBuf)
    #             firstComputed = True
    #     else:
    #         recBuf = ser.read(NUM_SAMPLES * 2)
    #         recBuf = convert_bytes_to_16bit_list(recBuf, NUM_SAMPLES)
    #         outBuf = audio_inject(outBuf, recBuf)

    #     # Convert uint16 to bytes
    #     outBuf = convert_16bit_to_bytes_struct(outBuf)
    #     sendQ.put(outBuf)
        



def main():
    global sendQ, chunks, chunk_id, ser, soundIsolate, running
    # Thread safe global queues
    sendQ = Queue(maxsize=1)

    # Music play stuff
    chunks = read_wav_as_uint16_chunks(chunk_size=NUM_SAMPLES)
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
    #receiveThread = threading.Thread(target=receive_fn)
    sendThread = threading.Thread(target=send_fn)
    #computeThread = threading.Thread(target=compute_fn)

    try:
        # Start threads
        #receiveThread.start()
        #computeThread.start()
        sendThread.start()
        
        firstComputed = False

        while running:
            outBuf = chunks[chunk_id]
            chunk_id += 1
            chunk_id = chunk_id % len(chunks)
            if not firstComputed:
                if ser.in_waiting >= NUM_SAMPLES * 2:
                    recBuf = ser.read(NUM_SAMPLES * 2)
                    recBuf = convert_bytes_to_16bit_list(recBuf, NUM_SAMPLES)
                    outBuf = audio_inject(outBuf, recBuf)
                    firstComputed = True
            else:
                recBuf = ser.read(NUM_SAMPLES * 2)
                recBuf = convert_bytes_to_16bit_list(recBuf, NUM_SAMPLES)
                outBuf = audio_inject(outBuf, recBuf)

            # Convert uint16 to bytes
            outBuf = convert_16bit_to_bytes_struct(outBuf)
            sendQ.put(outBuf)
    except KeyboardInterrupt:
        print('Ending threads')
        running = False
        sendThread.join()
        #computeThread.join()

    


if __name__ == '__main__':
    main()


    
