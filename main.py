#!/usr/bin/python3

# Mostly copied from https://picamera.readthedocs.io/en/release-1.13/recipes2.html
# Run this script, then point a web browser at http:<this-ip-address>:8000
# Note: needs simplejpeg to be installed (pip3 install simplejpeg).

import io
import logging
import socketserver
from http import server
from threading import Condition, Thread
import threading

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Import PiDog voice command components
from pidog_commands import process_text, my_dog
from transcribe_mic import get_speech_adaptation, transcribe_streaming

# Flag to control threads
running = True

def run_voice_commands():
    """Thread function to run voice command processing"""
    adaptation = get_speech_adaptation('phrases.txt')
    transcribe_streaming(sr=44100, callback=process_text, speech_adaptation=adaptation)

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
<script>
function process_command(text) {
    fetch('/process_command', {method: 'POST', body: JSON.stringify({text: text})})
        .then(response => {
            if (!response.ok) alert('Zoom failed');
        });
}
</script>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<button onclick=\"process_command('sit')\">Sit</button>
<button onclick=\"process_command('stand')\">Stand</button>
<button onclick=\"process_command('lie down')\">Lie Down</button>
<button onclick=\"process_command('bark')\">Bark</button>
<button onclick=\"process_command('shake')\">Shake</button><br/>
<button onclick=\"process_command('scratch')\">Scratch</button>
<button onclick=\"process_command('shake')\">Shake</button>
<button onclick=\"process_command('5')\">High Five</button>
<button onclick=\"process_command('pant')\">Pant</button>
<button onclick=\"process_command('sleep')\">Sleep</button>
<button onclick=\"process_command('push up')\">Push Up</button>

<button onclick=\"process_command('stretch')\">Stretch</button>
<button onclick=\"process_command('surprise')\">Surprise</button>
<button onclick=\"process_command('alert')\">Alert</button>
<button onclick=\"process_command('wag_tail')\">Wag Tail</button>
<button onclick=\"process_command('alert')\">Alert</button>
<button onclick=\"process_command('look left')\">Look Left</button>
<button onclick=\"process_command('look right')\">Look Right</button>
<button onclick=\"process_command('look down')\">Look Down</button>
<button onclick=\"process_command('look up')\">Look Up</button>
<button onclick=\"process_command('head reset')\">Head Reset</button>
<button onclick=\"process_command('no')\">Shake Head No</button>
<button onclick=\"process_command('yes')\">Shake Head Yes</button>
<button onclick=\"process_command('lick')\">Lick Hand</button>

<img src="stream.mjpg" width="1280" height="720" />
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
            import json
            data = json.loads(post_data)
            text = data.get('text', '')
            process_text(text)
            self.send_response(204)
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


for mode in sensor_modes:
    print("Mode", mode)
    
native_size = sensor_modes[1]['size']  # Usually the largest available
print(f"Native sensor size: {native_size}")
selected_mode = sensor_modes[0] #
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
picam2.set_controls({"ScalerCrop": (0, 0, scale_width, scale_height )})

# --- Start both the camera server and the voice command thread ---
if __name__ == '__main__':
    # Start the voice command thread
    voice_thread = Thread(target=run_voice_commands, daemon=True)
    voice_thread.start()

    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        picam2.stop_recording()
