import json
import os
import socket
import sys
import re
import time
import traceback
import urllib.request

sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../"))
from Monitor import Monitor  # noqa: E402, pylint: disable=C0413
from ores_config import config  # pylint: disable=E0611,W0614


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((config['host'], config['port']))
sock.settimeout(10)

M = Monitor()

pool = []
while True:
    try:
        starttime = time.time()
        while True:
            try:
                data, address = sock.recvfrom(config['max_bytes'])
                data = data.decode()
                data = json.loads(data)
                pool.append(data)
                if len(pool) >= 10 or time.time() - starttime > 10:
                    break
            except socket.timeout:
                break

        if len(pool):
            revids = '|'.join([str(data['revid']) for data in pool])
            url = 'https://ores.wikimedia.org/v3/scores/zhwiki/?models=damaging&revids={}'.format(revids)
            req = urllib.request.Request(url, headers={'User-Agent': M.wp_user_agent})
            result = urllib.request.urlopen(req).read().decode("utf8")
            result = json.loads(result)

            for data in pool:
                score = result['zhwiki']['scores'][str(data['revid'])]['damaging']['score']
                if score['prediction']:
                    summary = data['summary']
                    summary = re.sub(r'/\*.*?\*/', '', summary)
                    summary = re.sub(r'^\s+$', '', summary)
                    message = '{4:.0f}%（{3}）{1}（{5:+d}）{0}{2}'.format(
                        M.link_user(data['user']),
                        M.link_page(data['page']),
                        '' if summary == '' else '（' + M.parse_wikicode(summary) + '）',
                        M.link_diff(data['revid']),
                        score['probability']['true'] * 100,
                        data['length_diff'],
                    )
                    M.sendmessage(message, chat_id=config['chat_id'], token=config['token'])

            pool = []

    except Exception:
        traceback.print_exc()
        pool = []
