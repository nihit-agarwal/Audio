import numpy as np
import pyroomacoustics as pra
import soundfile as sf

# Load two audio sources (force mono)
sound1, fs1 = sf.read("sounds/cat.wav")
sound2, fs2 = sf.read("sounds/bird.mp3")

assert fs1 == fs2, "Sampling rates must match!"
fs = fs1  # Use common sampling rate

# Convert to mono if stereo
if len(sound1.shape) == 2:
    sound1 = np.mean(sound1, axis=1)
if len(sound2.shape) == 2:
    sound2 = np.mean(sound2, axis=1)

# Make both signals the same length
max_length = max(len(sound1), len(sound2))
sound1 = np.pad(sound1, (0, max_length - len(sound1)))
sound2 = np.pad(sound2, (0, max_length - len(sound2)))

# Define a shoebox room
room_dim = [5, 4, 3]  # 5m x 4m x 3m
room = pra.ShoeBox(room_dim, fs=fs, max_order=5, absorption=0.3)

# Define listener (binaural mic position)
listener_position = np.array([2.5, 2, 1.7])

# Left & Right ear positions (20 cm apart)
ear_left = listener_position + np.array([-0.1, 0, 0])
ear_right = listener_position + np.array([0.1, 0, 0])

# Add binaural microphone array
room.add_microphone_array(pra.MicrophoneArray(np.c_[ear_left, ear_right], fs))

# Define source positions
source1_position = np.array([1, 3, 1.5])
source2_position = np.array([4, 1, 1.5])

# Add sources
room.add_source(source1_position, signal=sound1)
room.add_source(source2_position, signal=sound2)

# Run the simulation
room.simulate()  #  This computes RIR and convolves automatically!

# Get the binaural signals (already convolved)
binaural_audio = np.column_stack((room.mic_array.signals[0], room.mic_array.signals[1]))

# Save the binaural output
sf.write("binaural_output.wav", binaural_audio, fs)

print(" Binaural simulation completed successfully!")
