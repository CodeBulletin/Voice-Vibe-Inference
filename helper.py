import numpy as np
import librosa

def reduce_sample_rate(data, sample_rate):
    if sample_rate == 16000:
        return data
    else:
        return librosa.resample(data, orig_sr=sample_rate, target_sr=16000)
    
def pad_to_length(data, length):
    if len(data) == length:
        return data
    elif len(data) > length:
        return data[:length]
    else:
        return np.pad(data, (0, length-len(data)), 'constant')
    
def convert_to_spectrogram(data):
    return librosa.stft(data, n_fft=512, hop_length=256)

def convert_to_mel_spectrogram(data):
    return librosa.feature.melspectrogram(y=data, sr=16000, n_fft=512, hop_length=256, n_mels=128)

def convert_to_mfcc(data):
    return librosa.feature.mfcc(y=data, sr=16000, n_fft=512, hop_length=256, n_mfcc=40)

def convert_to_mfcc_extra(data):
    # ZCR - Zero Crossing Rate
    result = np.array([])
    zcr = librosa.feature.zero_crossing_rate(data, frame_length=512, hop_length=256)
    result = np.hstack((result, np.mean(zcr.T, axis=0)))

    # RMS - Root Mean Square
    rms = librosa.feature.rms(y=data, frame_length=512, hop_length=256)
    result = np.hstack((result, np.mean(rms.T, axis=0)))

    # Chroma STFT - Chromagram of a short-time Fourier transform
    chroma_stft = librosa.feature.chroma_stft(y=data, sr=16000, n_fft=512, hop_length=256)
    result = np.hstack((result, np.mean(chroma_stft.T, axis=0)))

    # MFCC - Mel-frequency cepstral coefficients
    mfcc = convert_to_mfcc(data)
    result = np.hstack((result, np.mean(mfcc.T, axis=0)))

    # Mel Spectrogram
    mel_spectrogram = convert_to_mel_spectrogram(data)
    result = np.hstack((result, np.mean(mel_spectrogram.T, axis=0)))

    return result

def normalize(data):
    return (data - np.mean(data)) / np.std(data)