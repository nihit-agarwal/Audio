# Imports
import multiprocessing as mp
from multiprocessing import Process
import numpy as np
import soundfile as sf
import threading
import queue

import time
import matplotlib.pyplot as plt

# Read sound file
audio_file = "sounds/audio_mix_4.wav"
data, sample_rate = sf.read(audio_file, dtype="int16")


# Set the chunk size processed by model
CHUNK_SIZE = 512  # Number of samples per chunk processed
SAMPLE_RATE = 44100
BAUD_RATE = 1000000
# Thread-safe buffer (FIFO queue)
audio_queue = queue.Queue()
kill_process = queue.Queue()

# Duration of audio processed
processed_time = 0
time_taken = []




# **Receiver Thread** (Reads from Serial and pushes to queue)
def receive_audio():
    print("Receiving stereo audio...")
    timeSent = 0

    for i in range(0, len(data)):  
        chunk = data[i]  
        #time.sleep(1 / SAMPLE_RATE + 16 / BAUD_RATE)  # Simulate real-time streaming
        audio_queue.put(chunk)  # Push to queue
        timeSent += 1 / SAMPLE_RATE
        #print(f"Sent {timeSent:.3f}")
    
    print("Receiver stopped.")

# **Processing Thread** (Reads from queue, adjusts volume, and saves)
def process_audio():
    # Initialize the model to use for processing
    import audioML
    soundIsolate = audioML.AudioExtractor()
    soundIsolate.initialize_model()
    LABEL = "glass_breaking"
    print(f"Processing audio to extract {LABEL}")
    received_audio = []
    buffer = []
    processed_time = 0
    while True:
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
                print(f"Processed {processed_time} s")
        if processed_time >= 5.0:
            kill_process.put(True)
            break

    # Convert buffer to NumPy array and reshape into stereo format
    print(f"Average chunk processing time is {np.mean(time_taken)}")
    print(f"Median chunk processing time is {np.median(time_taken)}")
    print(f"Max chunk processing time is {max(time_taken)}")
    received_audio = np.array(received_audio, dtype=np.int16).reshape(-1, 2)
    
    # Save processed audio to a file
    sf.write("sounds/stereo_output.wav", received_audio, samplerate=SAMPLE_RATE)
    print("Processed stereo audio saved as stereo_output.wav")


def main_fn():
    # Start threads
    recv_thread = threading.Thread(target=receive_audio)
    process = Process(target=process_audio)

    recv_thread.start()
    process.start()

    time.sleep(2)
    # Wait for threads to finish (press Ctrl+C to stop)
    try:
        recv_thread.join()
        process.join()
        

    except KeyboardInterrupt:
        print("Stopping threads...")
        recv_thread.join()
        proc_thread.join()

if __name__ == '__main__':
    main_fn()
    
