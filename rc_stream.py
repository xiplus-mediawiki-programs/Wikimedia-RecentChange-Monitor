# -*- coding: utf-8 -*-
import json
import logging
import os
import socket
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

while True:
    try:
        for event in EventSource(url):
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                except ValueError:
                    continue

                data = event.data.encode()
                try:
                    sock.send(data)
                except Exception as e:
                    logging.error(e)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc(), noRaise=True)
