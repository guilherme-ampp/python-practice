"""
Just a backend service mock
"""
import threading
import time
import json
from threading import Event

class LongRunningTask():

    def __init__(self, socketio_callback):
        self.status = {'counting': 0}
        self.stop_event = Event()
        self.socketio_callback = socketio_callback

    def start(self):
        for _ in range(1000):
            self.status['counting'] += 1
            if self.socketio_callback:
                self.socketio_callback(json.dumps(self.status))
            time.sleep(1)
            if self.stop_event.is_set():
                break

    def stop(self):
        self.stop_event.set()
