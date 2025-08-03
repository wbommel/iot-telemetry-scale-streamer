from camserver.camera import Camera
from camserver.streamer import start_streaming_server
from camserver.mqtt_listener import WeightMonitor
import threading
import time

def main():
    camera = Camera()
    output = camera.get_output()

    threading.Thread(target=start_streaming_server, args=(output,), daemon=True).start()

    monitor = WeightMonitor(camera)
    monitor.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")

if __name__ == "__main__":
    main()