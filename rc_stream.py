# -*- coding: utf-8 -*-
import json
import logging
import os
import socket
import struct
import time
import traceback

from Monitor import Monitor
from rc_config import SOCKET_HOST, SOCKET_PORT
from sseclient import SSEClient as EventSource


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(filename)20s:%(lineno)4s] %(levelname)7s %(message)s')

os.environ['TZ'] = 'UTC'

url = 'https://stream.wikimedia.org/v2/stream/recentchange'

M = Monitor()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((SOCKET_HOST, SOCKET_PORT))

errorWaitTime = 1
while True:
    try:
        for event in EventSource(url):
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                except ValueError:
                    continue

                noError = True

                data = event.data.encode('utf-8')
                length = struct.pack('>Q', len(data))
                try:
                    sock.sendall(length)
                    sock.sendall(data)
                except Exception as e:
                    msg = 'Send {} bytes failed: {}. Wait {} seconds to retry'.format(len(data), e, errorWaitTime)
                    logging.error(msg)
                    M.error(msg)

                    time.sleep(errorWaitTime)
                    errorWaitTime *= 2
                    noError = False

                if noError and errorWaitTime > 1:
                    errorWaitTime //= 2

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc(), noRaise=True)
