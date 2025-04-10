# Imports
# Temporary fix for OpenMP dll issue (speechbrain related)
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
# Fix to use more cores for speechbrain
os.environ['NUMEXPR_MAX_THREADS'] = '9'

import torch
import dcc_tf_binaural as network
import utils
import soundfile as sf
import librosa
import numpy as np
import time
import matplotlib.pyplot as plt


class AudioExtractor:
    def __init__(self):
        self.model = None
        self.chunk_size = 256 # Number of samples 
        acceleration = torch.cuda.is_available()

        print("Acceleration: ", acceleration)
        if not acceleration:
            exit()
        torch.cuda.empty_cache()
        self.device = torch.device('cuda')
        self.enc_buf = None
        self.dec_buf = None
        self.out_buf = None
        self.labels = [
            "alarm_clock", "baby_cry", "birds_chirping", "cat", "car_horn", 
            "cock_a_doodle_doo", "cricket", "computer_typing", 
            "dog", "glass_breaking", "gunshot", "hammer", "music", 
            "ocean", "door_knock", "singing", "siren", "speech", 
            "thunderstorm", "toilet_flush"]
        self.birds = 2
        self.cat = 3
        self.label = None
        self.emb = None
        self.model_input = {'mixture': None, 'label_vector': None}
    
    def initialize_model(self, streaming=True):
        model = network.Net(label_len=20,
                        L=32,model_dim=256,
                        num_enc_layers=10,
                        num_dec_layers=1,
                        dec_buf_len=13,
                        dec_chunk_size=13,
                        use_pos_enc=True,
                        conditioning="mult",
                        out_buf_len=4)
        model.to(self.device)
        utils.load_checkpoint("model/39.pt", model, device=self.device)
        if streaming:
            self.enc_buf, self.dec_buf, self.out_buf = model.init_buffers(1, self.device)
        self.model = model
        return True
    

    def offline_test(self):
        if self.model == None:
            self.initialize_model(streaming=False)
            model = self.model
        y, sr = librosa.load("sounds/binaural_output.wav", sr=None, mono=False)
        print(f"shape: {y.shape} and type: {type(y[0][0])}")
        x = torch.tensor(y).unsqueeze(0)
        
        emb = torch.zeros(1,20)
        emb[0,2] = 1
        x = x.to(self.device)
        emb = emb.to(self.device)
        y = model({'mixture': x, 'label_vector': emb})
        numpy_array = y['x'].squeeze(0).cpu().detach()
        sf.write("sounds/bird_offline_test.wav", numpy_array.T, sr)

        
    def stream_test(self):
        # Check if model was initialized
        if self.model == None:
            self.initialize_model()
            model = self.model
        # Read test audio
        y, sr = sf.read("sounds/binaural_output.wav",dtype="float32")
        # List to stored final output
        processed_audio = []
        # Create the label vector
        emb = torch.zeros(1,20)
        emb[0,self.birds] = 1 
        emb = emb.to(self.device)
        # Emulate how the input stream audio would be
        y = y.flatten()
        # Stores time elapsed for each chunk
        time_arr = []
        for i in range(0, len(y) // 5, self.chunk_size):
            torch.cuda.synchronize()
            start = time.perf_counter()
            # Skip the last chunk if too small
            try:
                chunk = y[i : i + self.chunk_size].reshape(self.chunk_size // 2,2)
            except:
                continue
            # Create input structure
            chunk_tensor = torch.tensor(chunk.T, device=self.device, dtype=torch.float32).unsqueeze(0)
            model_input = {'mixture': chunk_tensor, 'label_vector': emb}
            # Run the model
            with torch.no_grad():
                output, self.enc_buf, self.dec_buf, self.out_buf = self.model(model_input, 
                                                                        self.enc_buf, 
                                                                        self.dec_buf, 
                                                                        self.out_buf)
            output_tensor = output['x']
            output_chunk = output_tensor.squeeze(0).T.to("cpu", non_blocking=True).detach()
            torch.cuda.synchronize()
            end = time.perf_counter()
            # Accumulate the audio
            processed_audio.extend(output_chunk.flatten())
            time_arr.append(end - start)

            del output, output_tensor, chunk_tensor
            torch.cuda.empty_cache()
            

        elapsed_time = np.mean(time_arr)
        print(f"Average chunk processing time: {elapsed_time:.6f} sec")
        processed_audio = np.array(processed_audio, dtype=np.float32).reshape(-1, 2)
        # Save the audio
        sf.write("sounds/bird_stream_test.wav", processed_audio, samplerate=sr)
        return np.median(time_arr)

    def int16_to_float32(self, chunk):
        return chunk.astype(np.float32) / 32768.0
    
    def float32_to_int16(self, chunk):
        return np.clip(chunk * 32768, -32768, 32767).astype(np.int16)
    
    def chunk_size_analysis(self):
        median_times = []
        chunk_sizes = []
        for i in range(5, 10):
            self.chunk_size = 2 ** i
            chunk_sizes.append(self.chunk_size)
            t = self.stream_test()

            median_times.append(t)
        plt.plot(chunk_sizes, median_times)
        plt.title('Median processing time vs chunk size')
        plt.xlabel('Chunk size')
        plt.ylabel('Median process time')
        plt.show()

            
    def run(self, label, chunk):
        # Check if model is initialized
        if self.model == None:
            self.initialize_model()
        # Create one hot encoded label vector
        if label != self.label:
            label_index = self.labels.index(label)
            emb = torch.zeros(1,20)
            emb[0,label_index] = 1
            self.emb = emb.to(self.device)
        
        #Log time
        #t_start = time.perf_counter()
        # Create input structure to pass as input to model
        chunk = self.int16_to_float32(chunk)
        chunk_tensor = torch.from_numpy(chunk).to(self.device, dtype=torch.float32).unsqueeze(0)
        
        self.model_input['mixture'] = chunk_tensor
        self.model_input['label_vector'] = self.emb
        torch.cuda.synchronize()
        # Run the model forward pass
        t_start = time.perf_counter()
        with torch.inference_mode():
            output, self.enc_buf, self.dec_buf, self.out_buf = self.model(self.model_input, 
                                                                    self.enc_buf, 
                                                                    self.dec_buf, 
                                                                    self.out_buf)
        
        torch.cuda.synchronize()
        t_end = time.perf_counter()
        #print(f'Inference time {t_end - t_start:.4f}')
        # Extract the audio output
        output_tensor = output['x'].squeeze(0).T
        #output_tensor = output['x'].squeeze(0).T.contiguous().pin_memory()

        output_chunk = output_tensor.to("cpu", non_blocking=True).detach().numpy()
        output_audio = self.float32_to_int16(output_chunk)
        #t_end = time.perf_counter()
        #del output, output_tensor, chunk_tensor
        #torch.cuda.empty_cache()
        return output_audio

if __name__ == '__main__':
    audioProcessor = AudioExtractor()
    audioProcessor.chunk_size_analysis()