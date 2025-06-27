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
function zoom() {
    fetch('/zoom', {method: 'POST'})
        .then(response => {
            if (!response.ok) alert('Zoom failed');
        });
}
</script>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<button onclick=\"process_text('sit')\">Sit</button><br/>
<button onclick=\"process_text('scratch')\">Scratch</button><br/>
<button onclick=\"process_text('shake')\">Shake</button><br/>
<button onclick=\"process_text('5')\">High Five</button><br/>
<button onclick=\"process_text('pant')\">Pant</button><br/>
<button onclick=\"process_text('sleep')\">Sleep</button><br/>
<button onclick=\"process_text('lie down')\">Lie Down</button><br/>
<button onclick=\"process_text('push up')\">Push Up</button><br/>
<button onclick=\"process_text('sit')\">Sit</button><br/>
<button onclick=\"process_text('stand')\">Stand</button><br/>
<button onclick=\"process_text('bark')\">Bark</button><br/>
<button onclick=\"process_text('shake')\">Shake</button><br/>
<button onclick=\"process_text('stretch')\">Stretch</button><br/>
<button onclick=\"process_text('surprise')\">Surprise</button><br/>
<button onclick=\"process_text('alert')\">Alert</button><br/><br/>
<button onclick=\"process_text('wag_tail')\">Wag Tail</button><br/>
<button onclick=\"process_text('sit')\">Alert</button><br/><br/>


<button onclick=\"process_text('look left')\">Look Left</button><br/>
<button onclick=\"process_text('look right')\">Look Right</button><br/>
<button onclick=\"process_text('look down')\">Look Down</button><br/>
<button onclick=\"process_text('look up')\">Look Up</button><br/>
<button onclick=\"process_text('head reset')\">Head Reset</button><br/>
<button onclick=\"process_text('no')\">Shake Head No</button><br/>
<button onclick=\"process_text('yes')\">Shake Head Yes</button><br/>
<button onclick=\"process_text('lick')\">Lick Hand</button><br/>

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
        if self.path == '/zoom':
            increment_zoom()
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
