"""
File to test different audio inputs for sound isolation
"""

import isolation.audioML as audioML
import numpy as np
import soundfile as sf

# Initialize the model to use for processing
soundIsolate = audioML.AudioExtractor()
soundIsolate.initialize_model()
soundIsolate.chunk_size = 512

sound_path = 'mixed_sounds/'
#input_files = ['filtered_output.wav', 'glass_speech.wav', 'cat_dog.wav']
input_files = ['micBirdViolin.wav']
input_files = [sound_path + f  for f in input_files]

output_files = []
#labels = ['cat', 'glass_breaking', 'cat']
labels = ['birds_chirping']

#f = open(input_files[1])
for i in range(len(input_files)):
    output_files.append(f"{input_files[i].split('.')[0]}_{labels[i]}_extracted.wav")



for i in range(len(input_files)):
    #label_num = soundIsolate.labels.index(labels[i])
    soundIsolate.stream_mono_test(input_files[i], output_files[i], labels[i])
    #time_arr = soundIsolate.stream_test(input_files[i], output_files[i], label_num)
    #print(np.min(time_arr), np.max(time_arr))


    



