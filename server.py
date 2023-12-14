import numpy as np
from flask import Flask, render_template, request, jsonify
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

UPLOAD_FOLDER = './temp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

# save model summary
with open('model_summary.txt', 'w') as f:
    model.summary(print_fn=lambda x: f.write(x + '\n'))

classes = np.loadtxt('classes.txt', dtype=str)
print(classes)

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

@app.route('/upload', methods=["post"])
def handle_audiofile():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # Classify audio file
    librosa_audio, librosa_sample_rate = librosa.load(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    reduce_sample_rate(librosa_audio, sample_rate)
    librosa_audio = pad_to_length(librosa_audio, int(sample_rate*time))
    mel = convert_to_mel_spectrogram(librosa_audio, sr=sample_rate)
    mel = np.pad(mel, ((0, 0), (0, mel_len - mel.shape[1])), 'constant', constant_values=0)
    value = predict(mel)

    return jsonify({'message': value}), 200



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