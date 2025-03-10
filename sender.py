import serial
import numpy as np
import soundfile as sf
import time

# Adjust the port name based on socat output
SERIAL_PORT = "/dev/ttys006"
BAUD_RATE = 115200
NUM_SAMPLES = 32  # Send 32 stereo frames (each frame has 2 samples: Left & Right)
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

# Send stereo audio in chunks
for i in range(0, len(data), NUM_SAMPLES * 2):  # 32 stereo frames = 64 samples
    numBatches += 1
    chunk = data[i : i + (NUM_SAMPLES * 2)]  # Extract 64 samples (L + R interleaved)
    ser.write(chunk.tobytes())  # Convert to bytes and send
    timeSent += NUM_SAMPLES / 44100
    print(f"Sent {len(chunk)//2} stereo frames ({len(chunk)} samples) and {numBatches} sent")
    time.sleep(0.001)  # Simulate real-time streaming
    #if numBatches == 4000:
    #    break

print("Stereo audio transmission complete")
ser.close()
