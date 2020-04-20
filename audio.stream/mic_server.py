#!/usr/bin/env python

import pyaudio
import socket
import select

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

def list_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    print("Input devices:")
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("- [{}] - {}".format(i, p.get_device_info_by_host_api_device_index(0, i).get('name')))


def server_main(input_index=None, port=4444):
    audio = pyaudio.PyAudio()

    if not input_index:
        list_devices()
        input_index = int(input("Input index: ")) or None

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('', int(port)))
    serversocket.listen(5)

    def callback(in_data, frame_count, time_info, status):
        for s in read_list[1:]:
            s.send(in_data)
        return (None, pyaudio.paContinue)


    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, 
                        frames_per_buffer=CHUNK, stream_callback=callback,
                        input_device_index=input_index)
    print("Streaming input[{}] at port [{}]".format(input_index, port))

    read_list = [serversocket]
    print("Capturing...")

    try:
        while True:
            readable, writable, errored = select.select(read_list, [], [])
            for s in readable:
                if s is serversocket:
                    (clientsocket, address) = serversocket.accept()
                    read_list.append(clientsocket)
                    print("Connection from", address)
                else:
                    data = s.recv(1024)
                    if not data:
                        read_list.remove(s)
    except KeyboardInterrupt:
        pass

    print("finished recording")

    serversocket.close()
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()