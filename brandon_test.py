"""
File to test different audio inputs for sound isolation
"""

import isolation.audioML as audioML
import numpy as np
import soundfile as sf

import os

# helper function that takes in path and returns an array of string paths to input audio files
def get_wav_files_and_labels(directory_path: str):
    """
    Returns:
        - A list of full paths to .wav files in the specified directory (non-recursive).
        - A list of tuples containing two labels extracted from each filename.
    
    Assumes filenames are in the format: label1-label2+optional.wav
    Example: 'computer_typing-thunderstorm+noise.wav' -> ('computer_typing', 'thunderstorm')
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"'{directory_path}' is not a valid directory.")
    
    wav_files = []
    labels = []

    for file in os.listdir(directory_path):
        if file.lower().endswith('.wav') and os.path.isfile(os.path.join(directory_path, file)):
            filepath = os.path.join(directory_path, file)
            name_without_ext = os.path.splitext(file)[0]

            # Remove any "+..." suffix
            name_clean = name_without_ext.split('+')[0]

            if '-' in name_clean:
                label1, label2 = name_clean.split('-', maxsplit=1)
                wav_files.append(filepath)
                labels.append((label1, label2))
            else:
                # Optionally skip or handle files without the expected pattern
                print(f"Warning: '{file}' does not match expected naming pattern. Skipped.")

    return wav_files, labels
    

# Initialize the model to use for processing
soundIsolate = audioML.AudioExtractor()
soundIsolate.initialize_model()
soundIsolate.chunk_size = 512

input_dir_path = 'brandon_test/input/'
output_dir_path = 'brandon_test/output/'


input_files, labels = get_wav_files_and_labels(input_dir_path)

print(input_files)
print(labels)

output_files = []

# create output files
for i in range(len(input_files)):
    base_name = os.path.splitext(os.path.basename(input_files[i]))[0]
    temp = []
    
    temp.append(f"{output_dir_path}{base_name}_{labels[i][0]}_extracted.wav")
    temp.append(f"{output_dir_path}{base_name}_{labels[i][1]}_extracted.wav")
    
    output_files.append(temp)
    
print(output_files)


time_arr = []
for i in range(len(input_files)):
    time_arr = soundIsolate.stream_test(input_files[i], output_files[i], label_num)
    
    first_label_num = soundIsolate.labels.index(labels[i][0])
    second_label_num = soundIsolate.labels.index(labels[i][1])
    
    time_arr.append(soundIsolate.stream_test(input_files[i], output_files[i][0], first_label_num))
    time_arr.append(soundIsolate.stream_test(input_files[i], output_files[i][1], second_label_num))
    


    



