import numpy as np
import soundfile as sf
def rms(signal):
    """Normalize signal to a target RMS value."""
    rms = np.sqrt(np.mean(signal ** 2))
    return rms

sound1, fs1 = sf.read("door_violin.wav")
rms1 = rms(sound1)
print('RMS of mixed signal is: ', rms1)


sound2, fs2 = sf.read('door_violin_cat_extracted.wav')
rms2 = rms(sound2)
print('RMS of extracted signal (no sound) is', rms2)

sound3, fs3 = sf.read('door_violin_door_knock_extracted.wav')
rms3 = rms(sound3)
print('RMS of extracted signal door knock is', rms3)