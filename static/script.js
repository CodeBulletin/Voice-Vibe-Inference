// const { SiriWave } = require('./siriwave.js');

const toggleButton = document.getElementById('toggleRecording');
const result = document.getElementById('result');
const filter = document.getElementById('bgg');
const file = document.getElementById('file');
const uploadFile = document.getElementById('UploadFile');

console.log(toggleButton);
console.log(result);
console.log(filter);


let mediaRecorder;
let audioChunks = [];
let actualChunks = [];
let recording = true;

var siriWave = new SiriWave({
    container: document.getElementById("siri"),
    width: 900,
    height: 400,
    style: 'ios9'
});

siriWave.setAmplitude(0);

// siriWave.stop();

// filter.classList.add('filter');

// WebSocket connection to the backend
// const socket = io.connect('http://' + document.domain + ':' + location.port);

// toggleButton.addEventListener('click', () => {
//     recording = !recording;
//     if (recording) {
//         startRecording();
//         filter.classList.remove('filter');
//         siriWave.start();
//     } else {
//         stopRecording();
//         filter.classList.add('filter');
//         siriWave.stop();
//     }
// });

// async function startRecording() {
//     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//     mediaRecorder = new MediaRecorder(stream,
//         { mimeType: 'audio/webm;codecs=opus' });

//     mediaRecorder.ondataavailable = (e) => {
//         if (e.data.size > 0) {
//             audioChunks.push(e.data);
//         }
//     };

//     mediaRecorder.onstop = () => {
//         // Convert audioChunks to a Blob
//         actualChunks = audioChunks.splice(0, audioChunks.length);

        
//         const audioBlob = new Blob(actualChunks, { type: 'audio/wav' });

//         // Send the audio data to the backend using socket.io

//         socket.emit('audio', audioBlob);

//         // Reset audioChunks
//         audioChunks = [];
//     }

//     mediaRecorder.start();
//     await new Promise((resolve) => setTimeout(resolve, 3500));
//     send_data();
// }

// function stopRecording() {
//     if (mediaRecorder && mediaRecorder.state === 'recording') {
//         mediaRecorder.stop();
//     }
// }

// // Get the response from the backend
// socket.on('response', function (data) {
//     result.innerHTML = data;
// });

// //Send the audio data to the backend every 3.5 seconds
// async function send_data() {
//     if (mediaRecorder && mediaRecorder.state === 'recording') {
//         mediaRecorder.stop();
//         mediaRecorder.start();
//         await new Promise((resolve) => setTimeout(resolve, 3500));
//         send_data();
//     }
// }

file.addEventListener('change', function () {
    if (this.files && this.files.length > 0) {
        // Send API request to the backend on \upload endpoint

        const formData = new FormData();
        formData.append('file', this.files[0]);

        let url = URL.createObjectURL(this.files[0]);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                result.innerHTML = data.message;
            })
            .catch(error => {
                console.error(error);
            });

        siriWave.setAmplitude(1.5);
        let audio = new Audio(url);
        audio.play();

        // On Audio end, stop the siriWave
        audio.onended = function () {
            siriWave.setAmplitude(0);
        };
    }
});
