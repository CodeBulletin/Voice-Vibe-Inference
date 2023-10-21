import numpy as np
import librosa
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from helper import pad_to_length, convert_to_mfcc_extra, normalize
import io
import random
import os

app = Flask(__name__)
socketio = SocketIO(app)

load_dotenv()

time = float(os.getenv('TIME'))
sample_rate = int(os.getenv('SAMPLE_RATE'))

# Check if temp folder exists and create it if not
if not os.path.exists('temp'):
    os.makedirs('temp')
 
def predict(spec): #placeholder
    return random.choice(['happy', 'sad', 'angry']) 

def random_file():
    return ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10)])

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio')
def handle_audio(audio_data):
    print('received audio')

    audio_bytes = io.BytesIO(audio_data)

    file = './temp/' + random_file() + '.wav'

    with open(file, 'wb') as f:
        f.write(audio_bytes.getbuffer())

    # Load the audio data
    audio_array, _ = librosa.load(file, sr=sample_rate, mono=True)

    #delete the file
    os.remove(file)

    # Generate and save the spectrogram
    spectrogram = convert_to_mfcc_extra(audio_array)
    spectrogram = normalize(spectrogram)

    print('spectrogram shape', spectrogram.shape)

    value = predict(spectrogram)

    emit('response', value)


if __name__ == '__main__':
    socketio.run(app)