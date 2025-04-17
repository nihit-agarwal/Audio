import serial
import struct
import threading
import time
import queue
from scipy.io import wavfile
import numpy as np

# === CONFIG ===
PORT = 'COM4'
BAUD_RATE = 3125000
SAMPLE_PERIOD_SEC = 3 / 44100  # ~181 µs for 8 samples at 44.1kHz
SAMPLE_BATCH_SIZE = 8  # 8 samples
USE_8BIT = False       # <<< Toggle this if you want 8-bit instead of 16-bit
AUDIO_FILE = 'output.wav'

# === SETUP SERIAL ===
ser = serial.Serial(
    port=PORT,
    baudrate=BAUD_RATE,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1
)

send_queue = queue.Queue()

def generate_tone_to_queue(frequency=1000, duration_sec=20.0, sample_rate=44100):
    print(f"Generating {frequency}Hz tone for {duration_sec}s at {sample_rate}Hz")
    
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    waveform = 0.8 * np.sin(2 * np.pi * frequency * t)  # amplitude < 1.0 to avoid clipping

    if USE_8BIT:
        # Normalize to [0, 255] for unsigned 8-bit
        data = ((waveform + 1.0) * 127.5).astype(np.uint8)
    else:
        # Normalize to unsigned 16-bit [0, 65535]
        data = ((waveform + 1.0) * 32767.5).astype(np.uint16)

    for i in range(0, len(data), SAMPLE_BATCH_SIZE):
        chunk = data[i:i + SAMPLE_BATCH_SIZE]
        if len(chunk) == SAMPLE_BATCH_SIZE:
            send_queue.put(chunk.tolist())

    print(f"Enqueued {send_queue.qsize()} chunks.")


def generate_square_wave_to_queue(frequency=800, duration_sec=2.0, sample_rate=44100):
    print(f"Generating {frequency}Hz square wave for {duration_sec}s at {sample_rate}Hz")

    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    waveform = 0.8 * np.sign(np.sin(2 * np.pi * frequency * t))  # square wave with ±0.8 amplitude

    if USE_8BIT:
        # Convert to uint8 [0, 255] from [-1, 1]
        data = ((waveform + 1.0) * 127.5).astype(np.uint8)
    else:
        # Convert to uint16 [0, 65535]
        data = ((waveform + 1.0) * 32767.5).astype(np.uint16)

    for i in range(0, len(data), SAMPLE_BATCH_SIZE):
        chunk = data[i:i + SAMPLE_BATCH_SIZE]
        if len(chunk) == SAMPLE_BATCH_SIZE:
            send_queue.put(chunk.tolist())

    print(f"Enqueued {send_queue.qsize()} square wave chunks.")

# === LOAD WAV FILE TO QUEUE ===
def load_wav_to_queue(filename):
    rate, data = wavfile.read(filename)
    print(f"Loaded WAV: {filename}")
    print(f"Sample rate: {rate}, Total samples: {len(data)}")

    # If stereo, take only left channel
    if data.ndim > 1:
        data = data[:, 0]

    if data.dtype == np.int16:
        if USE_8BIT:
            # Convert to float in [-1, 1], then to uint8 in [0, 255]
            data = ((data.astype(np.float32) / 32768.0 + 1.0) * 127.5).astype(np.uint8)
        else:
            # Convert to uint16 from int16 by offsetting
            data = (data.astype(np.int32) + 32768).astype(np.uint16)
    else:
        raise ValueError("Expected WAV to be int16 format")

    # Dummy data
    #data = np.array([i for i in range(1)] * 1000)
    # Chunking and queueing
    for i in range(0, len(data), SAMPLE_BATCH_SIZE):
        chunk = data[i:i + SAMPLE_BATCH_SIZE]
        if len(chunk) == SAMPLE_BATCH_SIZE:
            send_queue.put(chunk.tolist())

    print(f"Enqueued {send_queue.qsize()} chunks.")


# === SENDING THREAD ===
def sender_thread():
    total_sent = 0
    while not send_queue.empty():
        
        chunk = send_queue.get()

        if USE_8BIT:
            data = struct.pack('<8B', *chunk)
        else:
            data = struct.pack('<8H', *chunk)  # little-endian 16-bit unsigned

        #print(data)
        ser.write(data)
        total_sent += 1
        #input('press enter to send next')
        time.sleep(SAMPLE_PERIOD_SEC)

    print(f"Finished sending {total_sent * SAMPLE_BATCH_SIZE} samples.")
    ser.close()


# === MAIN ===
if __name__ == "__main__":
    generate_tone_to_queue()
    #load_wav_to_queue(AUDIO_FILE)
    #generate_square_wave_to_queue()
    input("Press Enter to start sending...")

    thread = threading.Thread(target=sender_thread)
    thread.start()
    thread.join()

    print("All done. Serial closed.")
