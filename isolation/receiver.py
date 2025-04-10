import serial
import numpy as np
import soundfile as sf
import threading
import queue
import audioML
import time
import matplotlib.pyplot as plt
# Adjust serial port names based on socat output
SERIAL_PORT = "COM4"
BAUD_RATE = 115200
# Adjust data ingestion rate
NUM_SAMPLES = 512  # 32 stereo frames (64 samples)
# Set the chunk size processed by model
CHUNK_SIZE = 1024  # Number of samples per chunk processed
SAMPLE_RATE = 44100

# Thread-safe buffer (FIFO queue)
audio_queue = queue.Queue()
running = True  # Flag to stop threads
shared_queue = queue.Queue()

# Duration of audio processed
processed_time = 0
time_taken = []

# Initialize the model to use for processing
soundIsolate = audioML.AudioExtractor()
soundIsolate.initialize_model()
LABEL = "glass_breaking"

ts = NUM_SAMPLES / 44100
# **Receiver Thread** (Reads from Serial and pushes to queue)
def receive_audio():
    global running
    global processed_time
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    
    print("Receiving stereo audio...")
    timeRec = 0
    while running: # and shared_queue.empty():
        if ser.in_waiting > NUM_SAMPLES * 4:
            timeRec += ts
            #print('Data incoming: ', ser.in_waiting)
            raw_data = ser.read(NUM_SAMPLES * 4)  # Read 32 stereo frames (64 samples, each 2 bytes)
            samples = np.frombuffer(raw_data, dtype=np.int16)  # Convert bytes to int16
            audio_queue.put(samples)  # Push to queued
        
        if timeRec > 5.99:
            running = False
        #time.sleep(0.001)
        #print(f"Buffered {len(samples)//2} stereo frames, {numBatches} received")

    ser.close()
    print("Receiver stopped.")

# **Processing Thread** (Reads from queue, adjusts volume, and saves)
def process_audio():
    
    print(f"Processing audio to extract {LABEL}")
    global running
    global processed_time
    global time_taken
    received_audio = []
    buffer = []
    while running or not audio_queue.empty():
        if not audio_queue.empty():
            samples = audio_queue.get()
            buffer.extend(samples)
            while len(buffer) >= CHUNK_SIZE:  # Ensure we have full stereo frames
                chunk = np.array(buffer[:CHUNK_SIZE], dtype=np.int16)
                buffer = buffer[CHUNK_SIZE:]  # Remove processed samples
                start = time.perf_counter() # Log start time

                input_audio_chunk = chunk.reshape(CHUNK_SIZE // 2, 2).T  # Shape (2, 32)
                ouput_audio_chunk = soundIsolate.run(LABEL, input_audio_chunk)
                
                # Accumulate the audio processed by model
                stop = time.perf_counter() # Log stop time
                received_audio.extend(ouput_audio_chunk.flatten())
                processed_time += (CHUNK_SIZE / 2) / SAMPLE_RATE
                
                time_taken.append(stop - start)
                #time_taken.append(delta_t)
                #print(f"Processed {processed_time} s")
        
    data_time = (CHUNK_SIZE /2 ) / SAMPLE_RATE 
    transmission_time = 0.003
    threshold = data_time - transmission_time

    # Convert buffer to NumPy array and reshape into stereo format
    time_taken = np.array(time_taken)
    print(f"Success rate: {np.sum(time_taken < threshold) / time_taken.shape}")
    received_audio = np.array(received_audio, dtype=np.int16).reshape(-1, 2)
    
    # Save processed audio to a file
    sf.write("sounds/stereo_output.wav", received_audio, samplerate=44100)
    print("Processed stereo audio saved as stereo_output.wav")

# Start threads
recv_thread = threading.Thread(target=receive_audio)
proc_thread = threading.Thread(target=process_audio)

recv_thread.start()
proc_thread.start()

# Wait for threads to finish (press Ctrl+C to stop)
try:
    recv_thread.join()
    proc_thread.join()
    plt.hist(time_taken, bins=10)
    plt.xlim(0.005, 0.010)
    plt.show()

except KeyboardInterrupt:
    print("Stopping threads...")
    running = False
    recv_thread.join()
    proc_thread.join()
    
