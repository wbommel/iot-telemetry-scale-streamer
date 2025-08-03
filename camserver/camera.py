from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from camserver.streamer import StreamingOutput
import threading
import time


class Camera:
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.configure(
            self.picam2.create_video_configuration(main={"size": (640, 480)})
        )
        self.streaming_output = StreamingOutput()
        self.picam2.start_recording(MJPEGEncoder(), FileOutput(self.streaming_output))
        self.capturing = False

    def get_output(self):
        return self.streaming_output

    def capture_still(self):
        now = datetime.now()
        date_str = now.strftime("%Y_%m_%d")
        time_str = now.strftime("%Y_%m_%d_%H_%M_%S")
        dir_path = Path.home() / "data" / "images" / date_str
        dir_path.mkdir(parents=True, exist_ok=True)
        filepath = dir_path / f"{time_str}.jpg"
        self.picam2.capture_file(str(filepath))
        print(f"Captured image: {filepath}")

    def start_interval_capture(self, stop_event, interval=15):
        def run():
            while not stop_event.is_set():
                self.capture_still()
                print(f"Next capture in {interval} seconds.")
                # stop_event.wait(interval)
                time.sleep(interval)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
