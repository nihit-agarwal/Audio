import soundfile as sf
from scipy.signal import butter, lfilter

# Design a low-pass Butterworth filter
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

# Apply the filter to the audio signal
def apply_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order)
    y = lfilter(b, a, data)
    return y

# File paths
input_file = 'D:\Audio\microCom\sounds\micRecorded.wav'
output_file = 'filtered_output_2.wav'

# Read WAV file
data, samplerate = sf.read(input_file)  # Assumes mono audio

# Filter
cutoff = 3000  # Cutoff frequency in Hz
filtered_data = apply_lowpass_filter(data, cutoff, samplerate)

# Write filtered audio
sf.write(output_file, filtered_data, samplerate)
print(f"Filtered mono audio saved to: {output_file}")
