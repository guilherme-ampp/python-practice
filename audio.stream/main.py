"""
Mic client and mic server with PyAudio

Dependencies on Ubuntu:
* sudo apt-get install libasound-dev
* Download the latest from http://www.portaudio.com/download.html
* Probably this one: http://www.portaudio.com/archives/pa_stable_v190600_20161030.tgz
* tar -xvf pa_stable_v190600_20161030.tgz
* sudo su root
* cd portaudio/
* ./configure
* make
* make install
* ldconfig
* pip install pyaudio
"""
import sys
import mic_server
import mic_client


if __name__ == "__main__":
    if 'list' in sys.argv[1]:
        mic_server.list_devices()
    elif 'server' in sys.argv[1]:
        mic_server.server_main()
    else:
        mic_client.client_main(sys.argv[1], sys.argv[2])
