import io
import logging
import socketserver
from http import server
import time
from threading import Condition
from config.settings import STREAM_PORT

PAGE = """<html>
<head>
<title>MJPEG Streaming</title>
</head>
<body>
<h1>MJPEG Streaming</h1>
<img src="stream.mjpg" width="640" height="480" />
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
        if self.path == "/":
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()
            try:
                while True:
                    with self.server.output.condition:
                        self.server.output.condition.wait()
                        frame = self.server.output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
                    time.sleep(0.1)
            except Exception as e:
                print(f"Removed streaming client {self.client_address}: {str(e)}")
                logging.warning("Removed streaming client %s: %s", self.client_address, str(e))

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def start_streaming_server(output):
    address = ("", STREAM_PORT)
    server = StreamingServer(address, StreamingHandler)
    server.output = output
    server.serve_forever()