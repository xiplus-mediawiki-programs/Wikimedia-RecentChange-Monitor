# -*- coding: utf-8 -*-
import json
import logging
import os
import socket
import struct
import traceback

from Monitor import Monitor
from rc_config import SOCKET_HOST, SOCKET_PORT
from sseclient import SSEClient as EventSource


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(filename)20s:%(lineno)4s] %(levelname)7s %(message)s')

os.environ['TZ'] = 'UTC'

url = 'https://stream.wikimedia.org/v2/stream/recentchange'

M = Monitor()

while True:
    try:
        for event in EventSource(url):
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                except ValueError:
                    continue

                data = event.data.encode('utf-8')
                length = struct.pack('>Q', len(data))
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((SOCKET_HOST, SOCKET_PORT))
                    sock.sendall(length)
                    sock.sendall(data)
                    sock.close()
                except Exception as e:
                    msg = 'Send {} bytes failed. {}'.format(len(data), e)
                    logging.error(msg)
                    M.error(msg)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc(), noRaise=True)
