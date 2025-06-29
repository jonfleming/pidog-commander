#!/usr/bin/python3
"""
Mock version of main.py for local testing without Pi hardware
Run this script to test the robot dog commander interface locally
"""


# Add argparse for command line parameter
import argparse

# Parse command line arguments early
parser = argparse.ArgumentParser(
    description="Mock PiDog Commander: By default, uses mock_hardware for local testing. Use --no-mock to run with real hardware modules instead of mocks."
)
parser.add_argument(
    '--no-mock',
    action='store_true',
    help='[ADVANCED] Skip patch_imports() and use real hardware modules instead of mocks. Only use this if you are running on a real Raspberry Pi with the required hardware.'
)
args, unknown = parser.parse_known_args()

# Enable mocking before importing hardware-dependent modules, unless --no-mock is set
if not args.no_mock:
    from mock_hardware import patch_imports
    patch_imports()

import io
import logging
import socketserver
from http import server
from threading import Condition, Thread
import threading
import json

# Now import the mocked modules
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Import mock PiDog voice command components
from pidog_commands import process_text, my_dog
from transcribe_mic_mock import get_speech_adaptation, transcribe_streaming

# Flag to control threads
running = True

def run_voice_commands():
    """Thread function to run voice command processing"""
    adaptation = get_speech_adaptation('phrases.txt')
    transcribe_streaming(sr=44100, callback=process_text, speech_adaptation=adaptation)

PAGE = """\
<html>
<head>
<title>Robo The Robot Dog (MOCK MODE)</title>
<script>
function process_command(text) {
    fetch('/process_command', {method: 'POST', body: JSON.stringify({text: text})})
        .then(response => {
            if (!response.ok) alert('Command failed');
        });
}

var recognition = null;

// Check if speech recognition is available
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    
    // Set continuous and interimResults attributes
    recognition.continuous = true;
    recognition.interimResults = true;
    
    // Define event handlers for the recognition process
    recognition.onstart = function() { 
        console.log('Speech recognition started');
        document.getElementById('speech-status').innerText = 'Listening...';
    }
    recognition.onresult = function(event) {
        var index = event.results.length - 1;
        var transcript = event.results[index][0].transcript;
        console.log('Recognized speech: ' + transcript);
        document.getElementById('last-command').innerText = 'Last command: ' + transcript;
        process_command(transcript);
    }
    recognition.onerror = function(event) { 
        console.error('Speech recognition error: ' + event.error);
        document.getElementById('speech-status').innerText = 'Error: ' + event.error;
    }
    recognition.onend = function() { 
        console.log('Speech recognition ended');
        document.getElementById('speech-status').innerText = 'Stopped';
    }
}

function toggleSpeechRecognition() {
    if (!recognition) {
        alert('Speech recognition not supported in this browser');
        return;
    }
    
    if (document.getElementById('speech-status').innerText === 'Listening...') {
        recognition.stop();
    } else {
        recognition.start();
    }
}

</script>
</head>
<body>
<h1>Robo The Robot Dog</h1>
<div style="margin: 10px 0;">
    <button onclick="toggleSpeechRecognition()" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
        Speech Recognition
    </button>
    <span id="speech-status" style="margin-left: 10px; font-weight: bold;">Ready</span>
</div>

<div id="last-command" style="margin: 10px 0; font-style: italic; color: #666;">
    Last command: None
</div>

<button onclick=\"process_command('lie down')\">Lie Down</button>
<button onclick=\"process_command('sit')\">Sit</button>
<button onclick=\"process_command('shake')\">Shake</button>
<button onclick=\"process_command('5')\">High Five</button>
<button onclick=\"process_command('lick')\">Lick Hand</button>
<button onclick=\"process_command('stand')\">Stand</button>
<button onclick=\"process_command('bark')\">Bark</button><br/>

<button onclick=\"process_command('pant')\">Pant</button>
<button onclick=\"process_command('howl')\">Howl</button>
<button onclick=\"process_command('sleep')\">Sleep</button>
<button onclick=\"process_command('twist')\">Twist</button>
<button onclick=\"process_command('pushup')\">Push Up</button>
<button onclick=\"process_command('surprise')\">Surprise</button>
<button onclick=\"process_command('wag tail')\">Wag Tail</button><br/>

<button onclick=\"process_command('think')\">Think</button>
<button onclick=\"process_command('no')\">Shake Head No</button>
<button onclick=\"process_command('yes')\">Shake Head Yes</button>
<button onclick=\"process_command('look left')\">Look Left</button>
<button onclick=\"process_command('look right')\">Look Right</button>
<button onclick=\"process_command('look down')\">Look Down</button>
<button onclick=\"process_command('look up')\">Look Up</button><br/>

<button onclick=\"process_command('forward')\">Forward</button>
<button onclick=\"process_command('backward')\">Backward</button>
<button onclick=\"process_command('turn left')\">Turn Left</button>
<button onclick=\"process_command('turn right')\">Turn Right</button>
<button onclick=\"process_command('alert')\">Alert</button>
<button onclick=\"process_command('attack')\">Attack</button>
<button onclick=\"process_command('reset')\">Reset</button>

<style>
    button {
        width: 120px;
        height: 40px;
        margin: 5px;
        border: 1px solid #ccc;
        border-radius: 5px;
        background-color: #f0f0f0;
        cursor: pointer;
    }
    button:hover {
        background-color: #e0e0e0;
    }
    button:active {
        background-color: #d0d0d0;
    }
    h3 {
        margin-top: 20px;
        color: #333;
    }
</style>

<h3>Mock Camera Feed</h3>
<img src="stream.mjpg" width="640" height="480" style="border: 2px solid #ccc; border-radius: 5px;" />

<div name="status" id="satus" style="margin-top: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">

</div>

</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    if frame is not None:
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', str(len(frame)))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/process_command':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                text = data.get('text', '')
                print(f"\n=== Web Command Received ===")
                print(f"Command: '{text}'")
                print("=" * 30)
                process_text(text)
                self.send_response(204)
                self.end_headers()
            except Exception as e:
                print(f"Error processing command: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

picam2 = Picamera2()
scale_width = 1280
scale_height = 960
sensor_modes = picam2.sensor_modes

def increment_zoom():
    pass

native_size = sensor_modes[1]['size']  # Usually the largest available
print(f"Native sensor size: {native_size}")
selected_mode = sensor_modes[0]
sensor_width, sensor_height = selected_mode['size']

# Configure video with a smaller output resolution to fit buffer
output_resolution = (640, 480)  # Adjust as needed for your buffer
config = picam2.create_video_configuration(
    main={"size": output_resolution, "format": 'XRGB8888'},    
    raw=selected_mode
)

picam2.configure(config)
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))
picam2.set_controls({"ScalerCrop": (0, 0, scale_width, scale_height)})

# --- Start both the camera server and the voice command thread ---
if __name__ == '__main__':
    print("\n" + "="*50)
    print("PIDOG COMMANDER")
    print("="*50)
    print("Starting web server on http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    # Start the voice command thread
    voice_thread = Thread(target=run_voice_commands, daemon=True)
    voice_thread.start()

    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        print("Server started successfully! Open http://localhost:8000 in your browser")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        print("Stopping camera...")
        picam2.stop_recording()
        print("Camera stopped.")