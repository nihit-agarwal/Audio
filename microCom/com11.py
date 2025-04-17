
"""
Testing data ingestion and sending
"""



import serial
import threading
import queue
import time
import struct

# Setup Serial Port
BAUD_RATE = 3125000
ser = serial.Serial(
    port='COM3',
    baudrate=BAUD_RATE,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1
)

# Constants
BLOCK_SIZE_BYTES = 1024           # 1024 bytes = 512 samples
SAMPLE_BATCH_SIZE = 8             # 8 samples = 16 bytes
SAMPLE_PERIOD_SEC = 68e-6         # 68 microseconds

# Send Queue
send_queue = queue.Queue()

# Dummy Processing Function (simulate 9ms work)
def process_data(samples):
    time.sleep(0.009)  # 9 ms
    return samples  # pass-through for now

# Convert 1024 bytes -> 512 uint16 samples
def convert_to_samples(raw_data):
    return list(struct.unpack('<512H', raw_data))  # little-endian uint16

# Thread 1: Receive and Process
def receiver_thread():
    while True:
        if ser.in_waiting >= BLOCK_SIZE_BYTES:
            raw_data = b''
            while len(raw_data) < BLOCK_SIZE_BYTES:
                raw_data += ser.read(BLOCK_SIZE_BYTES - len(raw_data))
            samples = convert_to_samples(raw_data)
            processed = process_data(samples)
            # Push into queue in chunks of 8 samples
            for i in range(0, len(processed), SAMPLE_BATCH_SIZE):
                chunk = processed[i:i + SAMPLE_BATCH_SIZE]
                send_queue.put(chunk)

# Thread 2: Timed Sender
def sender_thread():
    while True:
        try:
            chunk = send_queue.get(timeout=1)
            data = struct.pack('<8H', *chunk)  # Pack 8 uint16 samples
            ser.write(data)
        except queue.Empty:
            continue
        time.sleep(SAMPLE_PERIOD_SEC)

# Launch Threads
threading.Thread(target=receiver_thread, daemon=True).start()
threading.Thread(target=sender_thread, daemon=True).start()

# Keep Main Thread Alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ser.close()
    print("Serial closed.")
