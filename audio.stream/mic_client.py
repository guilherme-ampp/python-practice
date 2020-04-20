#!/usr/bin/env python
import pyaudio
import socket
import sys

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = int(200)

def client_main(address, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, int(port)))
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

    try:
        while True:
            data = s.recv(CHUNK)
            stream.write(data)
    except KeyboardInterrupt:
        pass

    print('Shutting down')
    s.close()
    stream.close()
    audio.terminate()


if __name__ == "__main__":
    client_main('localhost', 4444)
