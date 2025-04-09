'''
Threaded data transfer test
Receive data in 1 thread
Send data in 1 thread
Dummy process in another
'''

import threading
import serial
import queue
import time

# Serial comm Contstants
SERIAL_PORT = 'COM3'
BAUD_RATE = 1228800
SAMPLE_SIZE = 2 # Each sample is 2 bytes

# Audio properties
SAMPLE_RATE = 44100
T_STEP = 1 / SAMPLE_RATE

# Create thread safe queue
r_queue = queue.Queue()
s_queue = queue.Queue()
kill_process = queue.Queue()
# Create a serial port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)


def comm_fn():
    time_prev = 0
    frame_size = 2 * sample_size 
    while kill_process.empty():
        # Wait for 2 samples (L, R) to enter
        time_curr = time.perf_counter()
        if time_curr - time_prev >= T_STEP:
            time_prev = time.perf_counter()
            # Read data
            if ser.in_waiting >= frame_size:
                raw_data = ser.read(frame_size)
                samples = np.frombuffer(raw_data, dtype=np.int16)  # Convert bytes to int16
                r_queue.put(samples)  # Push nd array to queue
            # Send data
            samples = s_queue.get()
            ser.write(chunk.tobytes())
        
        

def process_fn():
    while kill_process.empty() or r_queue.qsize != 0:
        # Dummy process
        frame = r_queue.get()
        frame[0] *= 1
        frame[1] *= 2
        s_queue.put(frame)


    
def main_fn():
    communicator = threading.Thread(target=comm_fn)
    processor = threading.Thread(target=process_fn)

    time.sleep(10) # Run for 10 s
    kill_proces.put(True)
    communicator.join()
    processor.join()

if __name__ == '__main__':
    main_fn()
