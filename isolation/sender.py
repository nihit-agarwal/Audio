import serial
import numpy as np
import soundfile as sf
import time

# Adjust the port name based on socat output
SERIAL_PORT = "COM3"
BAUD_RATE = 6000000
NUM_SAMPLES = 512  # Send 32 stereo frames (each frame has 2 samples: Left & Right)
SAMPLE_RATE = 44100

# Load the stereo audio file
audio_file = "sounds/audio_mix_4.wav"
data, sample_rate = sf.read(audio_file, dtype="int16")
numBatches = 0
timeSent = 0
# Ensure the file is actually stereo
if len(data.shape) != 2 or data.shape[1] != 2:
    raise ValueError("Audio file must be stereo (2 channels)")

print(data.shape)
# Flatten interleaved stereo data (L1, R1, L2, R2, ...)
data = data.flatten()

# Open Serial Port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

ts = NUM_SAMPLES / SAMPLE_RATE
# Send stereo audio in chunks
total_start = time.perf_counter()
for i in range(0, len(data), NUM_SAMPLES * 2):  # 32 stereo frames = 64 samples
    start = time.perf_counter()
    numBatches += 1
    chunk = data[i : i + (NUM_SAMPLES * 2)]  # Extract 64 samples (L + R interleaved)
    ser.write(chunk.tobytes())  # Convert to bytes and send
    timeSent += ts
    stop = time.perf_counter()
    if stop - start < ts:
        time.sleep(ts - stop + start)
    #print(f"{timeSent} time sent and it took {stop - start:6f} time ")
    #time.sleep(NUM_SAMPLES / 44100)  # Simulate real-time streaming
    #if numBatches == 4000:
    #    break
total_stop = time.perf_counter()
print(f'{total_stop - total_start:4f} is the time elasped in transfer')
print("Stereo audio transmission complete")
ser.close()
