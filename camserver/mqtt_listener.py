import paho.mqtt.client as mqtt
import threading
from config.settings import MQTT_BROKER, MQTT_TOPIC, WEIGHT_THRESHOLD


class WeightMonitor:
    def __init__(self, camera):
        self.camera = camera
        self.stop_event = threading.Event()
        self.capture_thread = None
        self.active = False
        self.lock = threading.Lock()

    def _start_capture_thread(self):
        def run():
            print("Started interval capture thread.")
            self.camera.start_interval_capture(self.stop_event)
            print("Stopped interval capture thread.")

        self.stop_event.clear()
        self.capture_thread = threading.Thread(target=run, daemon=True)
        self.capture_thread.start()
        self.active = True

    def _stop_capture_thread(self):
        self.stop_event.set()
        self.active = False

    def on_message(self, client, userdata, msg):
        try:
            weight = float(msg.payload.decode())
            print(f"Received weight: {weight}")

            with self.lock:
                if weight > WEIGHT_THRESHOLD:
                    if not self.active:
                        print("Weight above threshold, starting capture interval.")
                        self._start_capture_thread()
                else:
                    if self.active:
                        print("Weight below threshold, stopping capture.")
                        self._stop_capture_thread()
        except ValueError:
            print("Received invalid weight value.")

    def start(self):
        client = mqtt.Client()
        client.connect(MQTT_BROKER)
        client.subscribe(MQTT_TOPIC)
        client.on_message = self.on_message
        client.loop_start()
