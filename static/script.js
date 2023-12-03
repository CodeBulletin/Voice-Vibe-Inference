const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const result = document.getElementById('result');

let mediaRecorder;
let audioChunks = [];
let actualChunks = [];

// WebSocket connection to the backend
const socket = io.connect('http://' + document.domain + ':' + location.port);

startButton.addEventListener('click', () => {
    startRecording();
    startButton.style.display = 'none';
    stopButton.style.display = 'block';
});

stopButton.addEventListener('click', () => {
    stopRecording();
    startButton.style.display = 'block';
    stopButton.style.display = 'none';
});

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream,
        { mimeType: 'audio/webm;codecs=opus' });

    mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
            audioChunks.push(e.data);
        }
    };

    mediaRecorder.onstop = () => {
        // Convert audioChunks to a Blob
        actualChunks = audioChunks.splice(0, audioChunks.length);

        
        const audioBlob = new Blob(actualChunks, { type: 'audio/wav' });

        // Send the audio data to the backend using socket.io

        socket.emit('audio', audioBlob);

        // Reset audioChunks
        audioChunks = [];
    }

    mediaRecorder.start();
    await new Promise((resolve) => setTimeout(resolve, 3500));
    send_data();
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }
}

// Get the response from the backend
socket.on('response', function (data) {
    result.innerHTML = data;
});

//Send the audio data to the backend every 3.5 seconds
async function send_data() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        mediaRecorder.start();
        await new Promise((resolve) => setTimeout(resolve, 3500));
        send_data();
    }
}