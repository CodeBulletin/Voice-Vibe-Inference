import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from helper import *
import io
import os
import pickle
import pydub

from tensorflow import keras

app = Flask(__name__)
socketio = SocketIO(app)

load_dotenv()

time = float(os.getenv('TIME'))
sample_rate = int(os.getenv('SAMPLE_RATE'))
mel_len = int(os.getenv('MEL_LEN'))

# load the model from disk
filepath = './models/RandomForest.pkl'
model = pickle.load(open(filepath, 'rb'))

model = keras.Sequential([

    # convolution layers
    keras.layers.Conv2D(256, (3, 3), activation="relu",
                        input_shape=(128, 274, 1)),
    keras.layers.MaxPooling2D((2, 2), strides=2),

    keras.layers.Conv2D(256, (3, 3), activation="relu",),
    keras.layers.MaxPooling2D((2, 2), strides=2),

    keras.layers.Conv2D(128, (3, 3), activation="relu"),
    keras.layers.MaxPooling2D((2, 2), strides=2),

    keras.layers.Conv2D(32, (3, 3), activation="relu"),
    keras.layers.MaxPooling2D((2, 2), strides=2),

    # fully connected classification
    # single vector
    keras.layers.Flatten(),

    # hidden layer and output layer
    keras.layers.Dense(1024, activation="relu"),
    keras.layers.Dense(512, activation="relu"),
    keras.layers.Dense(7, activation="softmax")
])

model.load_weights('./models/Model.h5')

classes = np.loadtxt('classes.txt', dtype=str)

# Check if temp folder exists and create it if not
if not os.path.exists('temp'):
    os.makedirs('temp')
 
def predict(spec): 
    spec = np.expand_dims(spec, axis=0)
    y = model.predict(spec, verbose=0)
    y = np.argmax(y)
    return classes[y]

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio')
def handle_audio(audio_data):
    print('received audio')

    sound = pydub.AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
    sound = sound.set_channels(1)
    sound = sound.set_frame_rate(sample_rate)

    audio_array = np.array(sound.get_array_of_samples(), dtype=np.float32)

    audio_array = pad_to_length(audio_array, int(sample_rate*time))

    mel = convert_to_mel_spectrogram(audio_array, sr=sample_rate)

    mel = np.pad(mel, ((0, 0), (0, mel_len - mel.shape[1])), 'constant', constant_values=0)

    value = predict(mel)

    emit('response', value)


if __name__ == '__main__':
    socketio.run(app)