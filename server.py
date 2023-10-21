import numpy as np
import librosa
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from helper import pad_to_length, convert_to_mfcc_extra, normalize
import io
from matplotlib import pyplot as plt

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio')
def handle_audio(audio_data):
    print('received audio')

    audio_bytes = io.BytesIO(audio_data)

    with open('audio.wav', 'wb') as f:
        f.write(audio_bytes.getbuffer())

    # Load the audio data
    audio_array, sample_rate = librosa.load('audio.wav', sr=16000)

    # Pad the audio data
    audio_array = pad_to_length(audio_array, int(3.5 * sample_rate))

    # Generate and save the spectrogram
    spectrogram = convert_to_mfcc_extra(audio_array)
    spectrogram = normalize(spectrogram)

    print(spectrogram.shape)

    emit('response', spectrogram.tolist())


if __name__ == '__main__':
    socketio.run(app)